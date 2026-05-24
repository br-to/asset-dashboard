import { readFileSync, writeFileSync, existsSync } from "fs";
import path from "path";

// 認証データはJSON fileに保存（ユーザー1人なので十分）
const DATA_PATH = path.join(process.cwd(), ".auth-data.json");

export interface StoredCredential {
  credentialID: string;
  credentialPublicKey: string; // base64
  counter: number;
  transports?: string[];
}

interface AuthData {
  registered: boolean;
  credentials: StoredCredential[];
  currentChallenge?: string;
}

function readData(): AuthData {
  if (!existsSync(DATA_PATH)) {
    return { registered: false, credentials: [] };
  }
  return JSON.parse(readFileSync(DATA_PATH, "utf-8"));
}

function writeData(data: AuthData): void {
  writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

export function isRegistered(): boolean {
  return readData().registered;
}

export function getCredentials(): StoredCredential[] {
  return readData().credentials;
}

export function addCredential(cred: StoredCredential): void {
  const data = readData();
  data.credentials.push(cred);
  data.registered = true;
  writeData(data);
}

export function updateCredentialCounter(credentialID: string, newCounter: number): void {
  const data = readData();
  const cred = data.credentials.find((c) => c.credentialID === credentialID);
  if (cred) {
    cred.counter = newCounter;
    writeData(data);
  }
}

export function setChallenge(challenge: string): void {
  const data = readData();
  data.currentChallenge = challenge;
  writeData(data);
}

export function getChallenge(): string | undefined {
  return readData().currentChallenge;
}
