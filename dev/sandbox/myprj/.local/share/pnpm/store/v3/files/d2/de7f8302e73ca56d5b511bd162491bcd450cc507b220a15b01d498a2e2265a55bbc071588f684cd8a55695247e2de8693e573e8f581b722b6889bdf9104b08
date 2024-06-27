"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.runUIMode = runUIMode;
var _server = require("playwright-core/lib/server");
var _utils = require("playwright-core/lib/utils");
var _compilationCache = require("../common/compilationCache");
var _multiplexer = require("../reporters/multiplexer");
var _teleEmitter = require("../reporters/teleEmitter");
var _reporters = require("./reporters");
var _tasks = require("./tasks");
var _utilsBundle = require("../utilsBundle");
var _list = _interopRequireDefault(require("../reporters/list"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
/**
 * Copyright Microsoft Corporation. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

class UIMode {
  constructor(config) {
    this._config = void 0;
    this._page = void 0;
    this._testRun = void 0;
    this.globalCleanup = void 0;
    this._globalWatcher = void 0;
    this._testWatcher = void 0;
    this._originalStderr = void 0;
    this._config = config;
    process.env.PW_LIVE_TRACE_STACKS = '1';
    config._internal.configCLIOverrides.forbidOnly = false;
    config._internal.configCLIOverrides.globalTimeout = 0;
    config._internal.configCLIOverrides.repeatEach = 0;
    config._internal.configCLIOverrides.shard = undefined;
    config._internal.configCLIOverrides.updateSnapshots = undefined;
    config._internal.listOnly = false;
    config._internal.passWithNoTests = true;
    for (const project of config.projects) project._internal.deps = [];
    for (const p of config.projects) p.retries = 0;
    config._internal.configCLIOverrides.use = config._internal.configCLIOverrides.use || {};
    config._internal.configCLIOverrides.use.trace = {
      mode: 'on',
      sources: false
    };
    this._originalStderr = process.stderr.write.bind(process.stderr);
    this._globalWatcher = new Watcher('deep', () => this._dispatchEvent({
      method: 'listChanged'
    }));
    this._testWatcher = new Watcher('flat', events => {
      const collector = new Set();
      events.forEach(f => (0, _compilationCache.collectAffectedTestFiles)(f.file, collector));
      this._dispatchEvent({
        method: 'testFilesChanged',
        params: {
          testFileNames: [...collector]
        }
      });
    });
  }
  async runGlobalSetup() {
    const reporter = new _multiplexer.Multiplexer([new _list.default()]);
    const taskRunner = (0, _tasks.createTaskRunnerForWatchSetup)(this._config, reporter);
    reporter.onConfigure(this._config);
    const context = {
      config: this._config,
      reporter,
      phases: []
    };
    const {
      status,
      cleanup: globalCleanup
    } = await taskRunner.runDeferCleanup(context, 0);
    await reporter.onExit({
      status
    });
    if (status !== 'passed') {
      await globalCleanup();
      return status;
    }
    this.globalCleanup = globalCleanup;
    return status;
  }
  async showUI() {
    this._page = await (0, _server.showTraceViewer)([], 'chromium', {
      app: 'watch.html',
      headless: (0, _utils.isUnderTest)() && process.env.PWTEST_HEADED_FOR_TEST !== '1'
    });
    if (!process.env.PWTEST_DEBUG) {
      process.stdout.write = chunk => {
        this._dispatchEvent({
          method: 'stdio',
          params: chunkToPayload('stdout', chunk)
        });
        return true;
      };
      process.stderr.write = chunk => {
        this._dispatchEvent({
          method: 'stdio',
          params: chunkToPayload('stderr', chunk)
        });
        return true;
      };
    }
    const exitPromise = new _utils.ManualPromise();
    this._page.on('close', () => exitPromise.resolve());
    let queue = Promise.resolve();
    this._page.exposeBinding('sendMessage', false, async (source, data) => {
      const {
        method,
        params
      } = data;
      if (method === 'exit') {
        exitPromise.resolve();
        return;
      }
      if (method === 'watch') {
        this._watchFiles(params.fileNames);
        return;
      }
      if (method === 'open' && params.location) {
        (0, _utilsBundle.open)('vscode://file/' + params.location).catch(e => this._originalStderr(String(e)));
        return;
      }
      if (method === 'resizeTerminal') {
        process.stdout.columns = params.cols;
        process.stdout.rows = params.rows;
        process.stderr.columns = params.cols;
        process.stderr.columns = params.rows;
        return;
      }
      if (method === 'stop') {
        this._stopTests();
        return;
      }
      queue = queue.then(() => this._queueListOrRun(method, params));
      await queue;
    });
    await exitPromise;
  }
  async _queueListOrRun(method, params) {
    if (method === 'list') await this._listTests();
    if (method === 'run') await this._runTests(params.testIds);
  }
  _dispatchEvent(message) {
    // eslint-disable-next-line no-console
    this._page.mainFrame().evaluateExpression(dispatchFuncSource, true, message).catch(e => this._originalStderr(String(e)));
  }
  async _listTests() {
    const listReporter = new _teleEmitter.TeleReporterEmitter(e => this._dispatchEvent(e));
    const reporter = new _multiplexer.Multiplexer([listReporter]);
    this._config._internal.listOnly = true;
    this._config._internal.testIdMatcher = undefined;
    const taskRunner = (0, _tasks.createTaskRunnerForList)(this._config, reporter, 'out-of-process');
    const context = {
      config: this._config,
      reporter,
      phases: []
    };
    (0, _compilationCache.clearCompilationCache)();
    reporter.onConfigure(this._config);
    const status = await taskRunner.run(context, 0);
    await reporter.onExit({
      status
    });
    const projectDirs = new Set();
    for (const p of this._config.projects) projectDirs.add(p.testDir);
    this._globalWatcher.update([...projectDirs], false);
  }
  async _runTests(testIds) {
    await this._stopTests();
    const testIdSet = testIds ? new Set(testIds) : null;
    this._config._internal.listOnly = false;
    this._config._internal.testIdMatcher = id => !testIdSet || testIdSet.has(id);
    const runReporter = new _teleEmitter.TeleReporterEmitter(e => this._dispatchEvent(e));
    const reporter = await (0, _reporters.createReporter)(this._config, 'ui', [runReporter]);
    const taskRunner = (0, _tasks.createTaskRunnerForWatch)(this._config, reporter);
    const context = {
      config: this._config,
      reporter,
      phases: []
    };
    (0, _compilationCache.clearCompilationCache)();
    reporter.onConfigure(this._config);
    const stop = new _utils.ManualPromise();
    const run = taskRunner.run(context, 0, stop).then(async status => {
      await reporter.onExit({
        status
      });
      this._testRun = undefined;
      this._config._internal.testIdMatcher = undefined;
      return status;
    });
    this._testRun = {
      run,
      stop
    };
    await run;
  }
  async _watchFiles(fileNames) {
    const files = new Set();
    for (const fileName of fileNames) {
      files.add(fileName);
      (0, _compilationCache.dependenciesForTestFile)(fileName).forEach(file => files.add(file));
    }
    this._testWatcher.update([...files], true);
  }
  async _stopTests() {
    var _this$_testRun, _this$_testRun$stop, _this$_testRun2;
    (_this$_testRun = this._testRun) === null || _this$_testRun === void 0 ? void 0 : (_this$_testRun$stop = _this$_testRun.stop) === null || _this$_testRun$stop === void 0 ? void 0 : _this$_testRun$stop.resolve();
    await ((_this$_testRun2 = this._testRun) === null || _this$_testRun2 === void 0 ? void 0 : _this$_testRun2.run);
  }
}
const dispatchFuncSource = String(message => {
  window.dispatch(message);
});
async function runUIMode(config) {
  var _uiMode$globalCleanup;
  const uiMode = new UIMode(config);
  const status = await uiMode.runGlobalSetup();
  if (status !== 'passed') return status;
  await uiMode.showUI();
  return (await ((_uiMode$globalCleanup = uiMode.globalCleanup) === null || _uiMode$globalCleanup === void 0 ? void 0 : _uiMode$globalCleanup.call(uiMode))) || 'passed';
}
function chunkToPayload(type, chunk) {
  if (chunk instanceof Buffer) return {
    type,
    buffer: chunk.toString('base64')
  };
  return {
    type,
    text: chunk
  };
}
class Watcher {
  constructor(mode, onChange) {
    this._onChange = void 0;
    this._watchedFiles = [];
    this._collector = [];
    this._fsWatcher = void 0;
    this._throttleTimer = void 0;
    this._mode = void 0;
    this._mode = mode;
    this._onChange = onChange;
  }
  update(watchedFiles, reportPending) {
    var _this$_fsWatcher;
    if (JSON.stringify(this._watchedFiles) === JSON.stringify(watchedFiles)) return;
    if (reportPending) this._reportEventsIfAny();
    this._watchedFiles = watchedFiles;
    (_this$_fsWatcher = this._fsWatcher) === null || _this$_fsWatcher === void 0 ? void 0 : _this$_fsWatcher.close().then(() => {});
    this._fsWatcher = undefined;
    this._collector.length = 0;
    clearTimeout(this._throttleTimer);
    this._throttleTimer = undefined;
    if (!this._watchedFiles.length) return;
    this._fsWatcher = _utilsBundle.chokidar.watch(watchedFiles, {
      ignoreInitial: true
    }).on('all', async (event, file) => {
      if (this._throttleTimer) clearTimeout(this._throttleTimer);
      if (this._mode === 'flat' && event !== 'add' && event !== 'change') return;
      if (this._mode === 'deep' && event !== 'add' && event !== 'change' && event !== 'unlink' && event !== 'addDir' && event !== 'unlinkDir') return;
      this._collector.push({
        event,
        file
      });
      this._throttleTimer = setTimeout(() => this._reportEventsIfAny(), 250);
    });
  }
  _reportEventsIfAny() {
    if (this._collector.length) this._onChange(this._collector.slice());
    this._collector.length = 0;
  }
}