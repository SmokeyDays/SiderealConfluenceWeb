import PubSub from 'pubsub-js';

export function pubMsg(title: string, str: string, type: 'success' | 'info' | 'warning' | 'error' = 'info', dur: number = 3) {
  PubSub.publish('alert-pubsub-message', {
    title: title,
    str: str,
    type: type,
    dur: dur,
    visible: true,
  });
};