import { socket } from '@/utils/connect';
import type { Factory } from './GameState';

export class FactoryLib {
  private factoryCache: { [key: string]: { [key: string]: Factory } } = {};
  private factoryDataListener: { [key: string]: { [key: string]: ((data: Factory) => void)[] } } = {};
  static instance: FactoryLib;

  constructor() {
    if (!FactoryLib.instance) {
      socket.on('factory-data', (data) => {
        this.factoryCache[data.room_name][data.factory.name] = data.factory;
        this.factoryDataPub(data.room_name, data.factory.name, data.factory);
      });
      FactoryLib.instance = this;
    }
    return FactoryLib.instance;
  }

  factoryDataPub(roomName: string, factoryName: string, data: Factory) {
    for (const listener of this.factoryDataListener[roomName][factoryName]) {
      listener(data);
    }
  }

  factoryDataSub(roomName: string, username: string, factoryName: string, listener: (data: Factory) => void) {
    if (!this.factoryDataListener[roomName]) {
      this.factoryDataListener[roomName] = {};
    }
    if (!this.factoryDataListener[roomName][factoryName]) {
      this.factoryDataListener[roomName][factoryName] = [];
    }
    this.factoryDataListener[roomName][factoryName].push(listener);
    socket.emit('query-factory', {
      room_name: roomName,
      username: username,
      factory_name: factoryName
    });
  }

  async getFactory(roomName: string, username: string, factoryName: string): Promise<Factory> {
    if (!this.factoryCache[roomName]) {
      this.factoryCache[roomName] = {};
    }
    if (this.factoryCache[roomName][factoryName]) {
      return this.factoryCache[roomName][factoryName];
    }
    return new Promise((resolve, reject) => {
      this.factoryDataSub(roomName, username, factoryName, (data: Factory) => {
        resolve(data);
      });
    });
  }
}

export const factoryLib = new FactoryLib();
