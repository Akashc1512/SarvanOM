/**
 * Mock for vis-data library
 */

export class DataSet {
  constructor(data = []) {
    this.data = Array.isArray(data) ? [...data] : [];
    this.listeners = {};
  }

  add(item) {
    if (Array.isArray(item)) {
      this.data.push(...item);
    } else {
      this.data.push(item);
    }
    this.emit('add', item);
  }

  remove(id) {
    const index = this.data.findIndex(item => item.id === id);
    if (index > -1) {
      const removed = this.data.splice(index, 1);
      this.emit('remove', removed);
      return removed;
    }
    return [];
  }

  update(item) {
    if (Array.isArray(item)) {
      item.forEach(i => this._updateSingle(i));
    } else {
      this._updateSingle(item);
    }
    this.emit('update', item);
  }

  _updateSingle(item) {
    const index = this.data.findIndex(d => d.id === item.id);
    if (index > -1) {
      this.data[index] = { ...this.data[index], ...item };
    } else {
      this.data.push(item);
    }
  }

  get(id) {
    if (id === undefined) {
      return [...this.data];
    }
    return this.data.find(item => item.id === id);
  }

  getIds() {
    return this.data.map(item => item.id);
  }

  clear() {
    this.data = [];
    this.emit('clear');
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

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }
}

export default {
  DataSet,
};