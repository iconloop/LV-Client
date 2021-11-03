import time
from assam.jwt import encrypt_jwe, decrypt_jwe_with_cek, encrypt_jwe_with_cek
from jwcrypto import jwk
from typing import Optional

from lvtool.consts import manager_pubkey


class Manager:
    def __init__(self, endpoint: str, locust_client):
        self._endpoint: str = endpoint if "http://" in endpoint else f"http://{endpoint}"
        self._key: jwk.JWK = jwk.JWK.from_json(manager_pubkey)
        self._locust_client = locust_client

    def _send(self, jwe_token, test_name, cek=None):
        response = self._locust_client.post(f"{self._endpoint}/vault", headers={
            "Authorization": jwe_token
        }, name=test_name)

        response_ = response.text[1:-1]  # remove quotes....

        if test_name == "VPR_0":
            header, decrypt_response = decrypt_jwe_with_cek(response_, cek)

            # print(f'decrypt_response({decrypt_response})')
            if decrypt_response['vp_request'] == {}:
                response.failure('There is no VP!')

        return response_

    def request_vpr(self) -> dict:
        payload = {
            "type": "BACKUP_REQUEST",
            "iat": int(time.time()),
            "did": "issuer did of phone auth"
        }
        jwe_token, cek = encrypt_jwe(self._key, payload)
        tokenized_response = self._send(jwe_token, "VPR_0", cek)
        header, backup_response = decrypt_jwe_with_cek(tokenized_response, cek)

        return backup_response

    def issue_vid_request(self, phone_number, vp=None):
        """Request VID and Storages.

        :param phone_number random phone number for load test virtual-user vID.
        :param vp: # TODO It must be replaced with a real client's one before starting the service.
        :return:
        """
        default_vp = {
            "@context": ["http://vc.zzeung.id/credentials/v1.json"],
            "id": "https://www.iconloop.com/vp/qnfdkqkd/123623",
            "type": ["PresentationResponse"],
            "fulfilledCriteria": {
                "conditionId": "uuid-requisite-0000-1111-2222",
                "verifiableCredential": "YXNzZGZhc2Zkc2ZkYXNhZmRzYWtsc2Fkamtsc2FsJ3NhZGxrO3N….",
                "verifiableCredentialParam": {
                    "@context": [
                        "http://vc.zzeung.id/credentials/v1.json",
                        "http://vc.zzeung.id/credentials/mobile_authentication/kor/v1.json"
                    ],
                    "type": ["CredentialParam", "MobileAuthenticationKorCredential"],
                    "credentialParam": {
                        "claim": {
                            "name": {
                                "claimValue": "이제니",
                                "salt": "d1341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "gender": {
                                "claimValue": "female",
                                "salt": "d1341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "telco": {
                                "claimValue": "SKT",
                                "salt": "345341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "phoneNumber": {
                                "claimValue": f"{phone_number}",
                                "salt": "a1341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "connectingInformation": {
                                "claimValue": "E21AEID0W6",
                                "salt": "b1341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "birthDate": {
                                "claimValue": "1985-02-28",
                                "salt": "af341c4b0cbff6bee9118da10d6e85a5"
                            },
                        },
                        "proofType": "hash",
                        "hashAlgorithm": "SHA-256"
                    }
                }
            }
        }

        vp = vp or default_vp

        payload = {
            "type": "ISSUE_VID_REQUEST",
            "iat": 1606125053,
            "vp": vp
        }

        jwe_token, cek = encrypt_jwe(self._key, payload)
        tokenized_response = self._send(jwe_token, "VPR_1")
        header, issue_vid_response = decrypt_jwe_with_cek(tokenized_response, cek)

        return issue_vid_response


class Storage:
    def __init__(self, storage_info: dict, locust_client):
        endpoint = storage_info['target']
        self._endpoint: str = endpoint if "http://" in endpoint else f"http://{endpoint}"
        self._key: jwk.JWK = jwk.JWK(**storage_info["key"])
        self._locust_client = locust_client

        # ---- Optional
        self._vID = None
        self._token: Optional[str] = storage_info.get("token")
        cek = storage_info.get("cek")
        self._cek: Optional[jwk.JWK] = jwk.JWK(**cek) if cek else None
        self._tag: Optional[str] = storage_info.get("tag")

    def _send(self, jwe_token, test_name):
        response = self._locust_client.post(f"{self._endpoint}/vault", headers={
            "Authorization": jwe_token
        }, name=test_name)

        assert response.status_code == 200
        return response.text[1:-1]  # remove quotes...

    def token_request(self, vID) -> dict:
        payload = {
            "type": "TOKEN_REQUEST",
            "iat": int(time.time()),
            "vID": vID,
            "vp": {"dujmmy": "vp"}  # TODO:
        }
        jwe_token, cek = encrypt_jwe(self._key, payload)
        tokenized_response = self._send(jwe_token, "TOKEN_0")
        header, token_response = decrypt_jwe_with_cek(tokenized_response, cek)

        self._vID = vID
        self._token = token_response["token"]
        self._cek = cek
        # print(f'In token_request vID({vID}), token({self._token})')

        return token_response

    def store_request(self, clue) -> dict:
        assert self._vID
        assert self._token
        assert self._cek

        payload = {
            "type": "STORE_REQUEST",
            "iat": int(time.time()),
            "vID": self._vID,
            "clue": clue,
            "token": self._token
        }
        # print(f'In store_request payload({payload})')
        jwe_token = encrypt_jwe_with_cek(self._cek, payload, kid=self._token)
        tokenized_response = self._send(jwe_token, "STORE_0")
        header, store_response = decrypt_jwe_with_cek(tokenized_response, self._cek)

        self._tag = store_response["tag"]

        return store_response

    def clue_request(self) -> dict:
        assert self._vID
        assert self._token
        assert self._cek

        payload = {
            "type": "CLUE_REQUEST",
            "iat": int(time.time()),
            "vID": self._vID,
            "token": self._token
        }
        if self._tag:
            payload["tag"] = self._tag

        # print(f'In clue_request payload({payload})')
        jwe_token = encrypt_jwe_with_cek(self._cek, payload, kid=self._token)
        tokenized_response = self._send(jwe_token, "CLUE_0")
        header, clue_response = decrypt_jwe_with_cek(tokenized_response, self._cek)

        return clue_response

    def to_json(self):
        obj = {
            "target": self._endpoint,
            "token": self._token,
            "key": self._key.export_public(as_dict=True),
            "cek": self._cek.export_symmetric(as_dict=True)
        }
        if self._tag:
            obj["tag"] = self._tag

        return obj
