/**
 * Mock for vis-network library
 */

export class Network {
  constructor(container, data, options) {
    this.container = container;
    this.data = data;
    this.options = options;
    this.listeners = {};
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      const index = this.listeners[event].indexOf(callback);
      if (index > -1) {
        this.listeners[event].splice(index, 1);
      }
    }
  }

  destroy() {
    this.listeners = {};
  }

  setData(data) {
    this.data = data;
  }

  setOptions(options) {
    this.options = options;
  }

  fit() {}
  
  focus() {}
  
  getPositions() {
    return {};
  }
}

export default {
  Network,
};