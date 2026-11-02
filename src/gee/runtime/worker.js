#!/usr/bin/env node
'use strict';

// SkillEvo-GEE headless execution worker. Run only trusted local scripts.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const HELP = `Read GEE JavaScript from a TXT file and request real cloud results.

Usage:
  node gee_execution_worker.js [options]

Options:
  --input FILE                 Required trusted local GEE JavaScript
  --output FILE                Required structured JSON report path
  --project ID                 Or EE_PROJECT; otherwise use the key's project_id
  --service-account-key FILE   Or EE_SERVICE_ACCOUNT_KEY / GOOGLE_APPLICATION_CREDENTIALS
  --proxy URL                  Or NODE_PROXY_URL / HTTPS_PROXY / HTTP_PROXY
                               Use --proxy direct to ignore proxy environment variables
  --timeout-sec N              Whole-run timeout (default: 180)
  --script-timeout-sec N       Local JavaScript timeout (default: 10)
  --sample-radius-m N          Radius around Map.setCenter (default: 300)
  --sample-scale-m N           Pixel statistics scale (default: 30)
  --help

Use print('name', eeObject) inside the TXT file. The runner calls evaluate(),
waits for all printed EE objects, and saves their actual returned values.
Map.addLayer(image) requests small-region pixel statistics for that layer.
Relative argument paths are resolved from your current working directory.
Only run trusted local scripts; node:vm is not a security sandbox.
`;

function parseArgs(argv) {
  const options = {
    input: '',
    output: '',
    project: process.env.EE_PROJECT || '',
    key: process.env.EE_SERVICE_ACCOUNT_KEY || process.env.GOOGLE_APPLICATION_CREDENTIALS || '',
    proxy: process.env.NODE_PROXY_URL || process.env.HTTPS_PROXY ||
      process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy || '',
    timeoutSec: 180,
    scriptTimeoutSec: 10,
    sampleRadiusM: 300,
    sampleScaleM: 30,
  };
  const fields = {
    '--input': 'input', '--output': 'output', '--project': 'project',
    '--service-account-key': 'key', '--proxy': 'proxy',
    '--timeout-sec': 'timeoutSec', '--script-timeout-sec': 'scriptTimeoutSec',
    '--sample-radius-m': 'sampleRadiusM', '--sample-scale-m': 'sampleScaleM',
  };
  for (let i = 0; i < argv.length; i++) {
    const flag = argv[i];
    if (flag === '--help') { options.help = true; continue; }
    if (!fields[flag]) throw new Error(`Unknown option: ${flag}`);
    const value = argv[++i];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${flag}`);
    options[fields[flag]] = value;
  }
  for (const field of ['timeoutSec', 'scriptTimeoutSec']) {
    options[field] = Number(options[field]);
    if (!Number.isFinite(options[field]) || options[field] <= 0 ||
        options[field] * 1000 > 2147483647) {
      throw new Error(`${field} must be positive and no greater than 2147483 seconds`);
    }
  }
  for (const field of ['sampleRadiusM', 'sampleScaleM']) {
    options[field] = Number(options[field]);
    if (!Number.isFinite(options[field]) || options[field] <= 0) {
      throw new Error(`${field} must be a positive number`);
    }
  }
  if (!options.input || !options.output) {
    throw new Error('--input and --output are required');
  }
  options.input = path.resolve(options.input);
  options.output = path.resolve(options.output);
  if (options.key) options.key = path.resolve(options.key);
  if (options.input === options.output || (options.key && options.key === options.output)) {
    throw new Error('--output must differ from the input and credential files');
  }
  return options;
}

function errorText(error) {
  if (error instanceof Error || (error && typeof error.message === 'string')) {
    return error.message;
  }
  return typeof error === 'string' ? error : JSON.stringify(error);
}

async function configureProxy(proxyUrl) {
  if (!proxyUrl || proxyUrl === 'direct') return;
  const {HttpsProxyAgent} = await import('https-proxy-agent');
  const https = require('node:https');
  const agent = new HttpsProxyAgent(proxyUrl);
  // Patch before loading EE, including requests made during authentication.
  for (const method of ['request', 'get']) {
    const original = https[method];
    https[method] = function (...args) {
      if (typeof args[0] === 'string' || args[0] instanceof URL) {
        if (args[1] && typeof args[1] === 'object') {
          args[1] = {...args[1], agent};
        } else {
          args.splice(1, 0, {agent});
        }
      } else {
        args[0] = {...args[0], agent};
      }
      return original.apply(this, args);
    };
  }
  console.error(`[GEE] Proxy enabled: ${new URL(proxyUrl).host}`);
}

async function main(options) {
  const started = Date.now();
  const report = {
    status: 'running',
    phase: 'setup',
    input: options.input,
    project: options.project || null,
    started_at: new Date(started).toISOString(),
    timeout_sec: options.timeoutSec,
    outputs: [],
  };
  let finished = false;
  let deadline;

  function finish(error) {
    if (finished) return;
    finished = true;
    clearTimeout(deadline);
    for (const output of report.outputs) {
      if (output.status === 'pending' || output.status === 'running') {
        output.status = 'failed';
        output.error = errorText(error || 'Run ended before this output completed');
      }
    }
    report.cloud_success_count = report.outputs.filter(
      output => output.source === 'earth_engine' && output.status === 'success'
    ).length;
    report.cloud_failure_count = report.outputs.filter(
      output => output.source === 'earth_engine' && output.status === 'failed'
    ).length;
    report.status = error || report.outputs.some(output => output.status === 'failed')
      ? 'failed' : 'success';
    if (error) report.error = errorText(error);
    report.finished_at = new Date().toISOString();
    report.elapsed_ms = Date.now() - started;
    try {
      fs.mkdirSync(path.dirname(options.output), {recursive: true});
      fs.writeFileSync(options.output, JSON.stringify(report, null, 2) + '\n', 'utf8');
      console.error(`[GEE] ${report.status}; result: ${options.output}`);
    } catch (writeError) {
      console.error(`[GEE] Cannot save result: ${errorText(writeError)}`);
      process.exit(1);
    }
    if (report.error) console.error(`[GEE] ${report.error}`);
    // Close idle SDK connections, including after a hard deadline.
    process.exit(report.status === 'success' ? 0 : 1);
  }

  deadline = setTimeout(() => {
    finish(new Error(`Whole-run timeout after ${options.timeoutSec}s during ${report.phase}`));
  }, options.timeoutSec * 1000);

  try {
    if (!options.key) {
      throw new Error('Provide --service-account-key or set EE_SERVICE_ACCOUNT_KEY');
    }
    const source = fs.readFileSync(options.input, 'utf8').replace(/^\uFEFF/, '');
    // Compile before authentication, so syntax errors do not send requests.
    const script = new vm.Script(source, {filename: options.input});
    const key = JSON.parse(fs.readFileSync(options.key, 'utf8').replace(/^\uFEFF/, ''));
    if (!key.client_email || !key.private_key) {
      throw new Error('Credential JSON must contain client_email and private_key');
    }
    report.project = options.project || key.project_id;
    if (!report.project) throw new Error('Provide --project or set EE_PROJECT');

    await configureProxy(options.proxy);
    const ee = require('@google/earthengine');
    ee.data.setDeadline(options.timeoutSec * 1000);
    report.phase = 'authentication';
    console.error('[GEE] Authenticating service account...');
    await new Promise((resolve, reject) => {
      ee.data.authenticateViaPrivateKey(key, resolve, reject);
    });
    report.phase = 'initialization';
    await new Promise((resolve, reject) => {
      ee.initialize(null, null, resolve, reject, null, report.project);
    });

    const queued = [];
    let printIndex = 0;
    let layerIndex = 0;
    let mapCenter = null;
    function print(...values) {
      printIndex += 1;
      const label = values.length > 1 && typeof values[0] === 'string'
        ? values.shift() : `print_${printIndex}`;
      for (let index = 0; index < values.length; index++) {
        const value = values[index];
        const output = {
          name: values.length > 1 ? `${label}[${index + 1}]` : label,
          source: value instanceof ee.ComputedObject ? 'earth_engine' : 'javascript',
          status: 'pending',
        };
        report.outputs.push(output);
        queued.push({value, output});
      }
    }

    const map = {
      setCenter(lon, lat, zoom) {
        if (!Number.isFinite(lon) || !Number.isFinite(lat) ||
            lon < -180 || lon > 180 || lat < -90 || lat > 90) {
          throw new Error('Map.setCenter requires valid numeric longitude and latitude');
        }
        mapCenter = [lon, lat];
        report.map_center = {longitude: lon, latitude: lat, zoom};
        return map;
      },
      addLayer(image, visParams, name) {
        if (!(image instanceof ee.Image)) {
          throw new Error('The headless worker supports only ee.Image for Map.addLayer');
        }
        layerIndex += 1;
        const output = {
          name: name || `layer_${layerIndex}`,
          source: 'earth_engine',
          sink: 'Map.addLayer',
          result_kind: 'small_region_pixel_statistics',
          status: 'pending',
        };
        report.outputs.push(output);
        queued.push({
          output,
          makeValue() {
            if (!mapCenter) {
              throw new Error('Layer statistics require Map.setCenter(lon, lat, zoom) in the TXT');
            }
            const selectedBands = visParams && visParams.bands;
            const selected = selectedBands ? image.select(selectedBands) : image;
            const region = ee.Geometry.Point(mapCenter).buffer(options.sampleRadiusM);
            output.validation_region = {
              center: mapCenter,
              radius_m: options.sampleRadiusM,
              scale_m: options.sampleScaleM,
              crs: 'EPSG:3857',
              bands: selectedBands || 'all',
            };
            // Validate real pixels with a small projected request, not metadata.
            return selected.reduceRegion({
              reducer: ee.Reducer.mean()
                .combine({reducer2: ee.Reducer.minMax(), sharedInputs: true})
                .combine({reducer2: ee.Reducer.count(), sharedInputs: true}),
              geometry: region,
              scale: options.sampleScaleM,
              crs: 'EPSG:3857',
              maxPixels: 100000,
            });
          },
        });
        return map;
      },
    };

    report.phase = 'local_javascript';
    console.error(`[GEE] Executing TXT: ${options.input}`);
    const context = vm.createContext({
      ee,
      print,
      Map: map,
      console: {log: print, info: print, warn: print, error: print},
    });
    script.runInContext(context, {timeout: Math.max(1, Math.floor(options.scriptTimeoutSec * 1000))});
    if (!queued.some(item => item.output.source === 'earth_engine')) {
      throw new Error("No EE output found. Use print('name', eeObject) or Map.addLayer(image) in the TXT.");
    }

    report.phase = 'cloud_evaluation';
    await Promise.all(queued.map(async ({value, makeValue, output}) => {
      const outputStarted = Date.now();
      output.status = 'running';
      try {
        if (makeValue) value = makeValue();
        const result = output.source === 'earth_engine'
          ? await new Promise((resolve, reject) => {
            // This is a real Earth Engine compute request, not serialize().
            value.evaluate((success, failure) => {
              if (failure) reject(new Error(errorText(failure)));
              else resolve(success);
            });
          })
          : value;
        // Store plain JSON values; never serialize an EE expression as a result.
        const encoded = JSON.stringify(result);
        if (encoded === undefined) throw new Error('Output is not a JSON value');
        output.value = JSON.parse(encoded);
        output.status = 'success';
        console.log(`[${output.name}] ${encoded}`);
      } catch (error) {
        output.status = 'failed';
        output.error = errorText(error);
        console.error(`[${output.name}] FAILED: ${output.error}`);
      } finally {
        output.elapsed_ms = Date.now() - outputStarted;
      }
    }));
    report.phase = 'complete';
    finish();
  } catch (error) {
    finish(error);
  }
}

try {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) console.log(HELP);
  else main(options).catch(error => {
    console.error(errorText(error));
    process.exit(1);
  });
} catch (error) {
  console.error(errorText(error));
  process.exitCode = 1;
}
