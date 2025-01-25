import axios from 'axios';
import { ConfigType } from './dto';

const BASE_URL = `https://${window.location.hostname}:4000`;

function HandleError(error: any) {
  if (error.response) {
    return { error: 'Server Error', statusCode: error.response.status };
  } else if (error.request) {
    return { error: 'No response from server' };
  } else {
    return { error: 'Request setup error', message: error.message };
  }
}

export async function GetVoices() {
  try {
    const response = await axios.get(`${BASE_URL}/get_voices`);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function GetVoiceSample(voice: { [x: string]: any }) {
  const url =
    `https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/` +
    `${voice['language']['family']}/` +
    `${voice['language']['code']}/` +
    `${voice['name']}/` +
    `${voice['quality']}/samples/speaker_0.mp3?download=true`;

  try {
    const response = await axios.get(url, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function GetConfig() {
  try {
    const response = await axios.get(`${BASE_URL}/config`);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function PostConfig(config: ConfigType) {
  try {
    const response = await axios.post(`${BASE_URL}/config`, { config: config });
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function PostAssistantData(data: any) {
  try {
    const response = await axios.post(`${BASE_URL}/save_assistant`, data);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function DeleteAssistant(assistantId: string) {
  try {
    const response = await axios.delete(`${BASE_URL}/delete_assistant`, {
      data: assistantId,
      headers: { 'Content-Type': 'text/plain' },
    });
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function GetCustomCommands() {
  try {
    const response = await axios.get(`${BASE_URL}/get_custom_commands`);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function PostCustomCommand(data: any) {
  try {
    const response = await axios.post(`${BASE_URL}/custom_command`, data);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function DeleteCustomCommand(key: string) {
  try {
    const response = await axios.delete(`${BASE_URL}/custom_command`, { data: key });
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}

export async function GetOpenaiModels() {
  try {
    const response = await axios.get(`${BASE_URL}/get_openai_models`);
    return response.data;
  } catch (error) {
    return HandleError(error);
  }
}
