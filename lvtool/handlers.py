import hashlib
import json
import logging
from typing import List

from .helper import read_input_file, read_clue_file
from .interfaces import Manager, Storage
from .types import Commands

logging.basicConfig(level=logging.INFO)


class Handler:
    def __init__(self):
        self.managers = {}
        self.storages = {}

    def get_manager(self, endpoint):
        if endpoint in self.managers:
            return self.managers[endpoint]
        self.managers[endpoint] = Manager(endpoint)
        return self.managers[endpoint]

    def get_storage(self, storage_info):
        if storage_info['target'] in self.storages:
            return self.storages[storage_info['target']]
        self.storages[storage_info['target']] = Storage(storage_info)
        return self.storages[storage_info['target']]

    def _handle_get_vp(self, args):
        output_path = args.output

        manager = self.get_manager(endpoint=args.endpoint)
        logging.debug("- Requesting VPR...")
        vpr: dict = manager.request_vpr()  # TODO: THIS should contain VPRequest.
        logging.debug(f"- VPR Response: {vpr}")
        with open(output_path, "w") as f:
            f.write(json.dumps(vpr, indent=4))

    def _handle_get_storages(self, args):
        vp = None  # TODO: Make VP by VPR from lv-manager.

        if args.vp:
            logging.debug(f"Use User VP({args.vp})")
            vp = read_input_file(args.vp)
        else:
            logging.debug("Use Default VP")

        output_path = args.output

        manager = self.get_manager(endpoint=args.endpoint)
        logging.debug("- Requesting VID...")
        vid_response = manager.issue_vid_request(vp)  # TODO: Fill VID Request according to responded VPR!
        logging.debug(f"- VID Response: {vid_response}")

        with open(output_path, "w") as f:
            f.write(json.dumps(vid_response, indent=4))

    def _handle_token(self, args):
        vid_response_msg: dict = read_input_file(args.input)
        storages: List[dict] = []
        vID = vid_response_msg["vID"]

        for storage_info in vid_response_msg["storages"]:
            storage = self.get_storage(storage_info)
            storage.token_request(vID)
            storages.append(storage.to_json())

        with open(args.output, "w") as f:
            f.write(json.dumps({
                "vID": vid_response_msg["vID"],
                "recovery_key": vid_response_msg["recovery_key"],
                "storages": storages
            }, indent=4))

    def _handle_store(self, args):
        clues: List[str] = read_clue_file(args.clues)
        vid_response_msg: dict = read_input_file(args.input)
        storages: List[dict] = []

        for clue, storage_info in zip(clues, vid_response_msg["storages"]):
            storage = self.get_storage(storage_info)
            storage.store_request(vid_response_msg["vID"], clue)
            storages.append(storage.to_json())

        with open(args.output, "w") as f:
            f.write(json.dumps({
                "vID": vid_response_msg["vID"],
                "recovery_key": vid_response_msg["recovery_key"],
                "storages": storages
            }, indent=4))

    def _handle_read(self, args):
        vid_response_msg: dict = read_input_file(args.input)
        storages = (self.get_storage(storage_info) for storage_info in vid_response_msg["storages"])
        gathered_clues = []

        for storage in storages:
            response = storage.clue_request(vid_response_msg["vID"])
            gathered_clues.append(response["clue"])

        with open(args.output, "w") as f:
            f.writelines("\n".join(gathered_clues))

    def _handle_make_vp(self, args):
        logging.debug(f"userid({args.userid}) hashed({hashlib.sha256(args.userid.encode('UTF-8')).hexdigest()})")
        logging.debug(f"pin({args.pin}) hashed({hashlib.sha256(args.pin.encode('UTF-8')).hexdigest()})")

        userid = hashlib.sha256(args.userid.encode('UTF-8')).hexdigest()
        pin = hashlib.sha256(args.pin.encode('UTF-8')).hexdigest()

        user_vp = {
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
                    "type": ["UserParam", "MalformedUserParam"],
                    "userParam": {
                        "claim": {
                            "userId": {
                                "claimValue": userid,
                                "salt": "d1341c4b0cbff6bee9118da10d6e85a5"
                            },
                            "pin": {
                                "claimValue": pin,
                                "salt": "d1341c4b0cbff6bee9118da10d6e85a5"
                            }
                        },
                        "proofType": "hash",
                        "hashAlgorithm": "SHA-256"
                    }
                }
            }
        }

        with open(f"vp_{args.userid}.json", "w") as f:
            json.dump(user_vp, f, indent=4)

    def __call__(self, command, args):
        handlers = {
            Commands.VPR: self._handle_get_vp,
            Commands.VID: self._handle_get_storages,
            Commands.TOKEN: self._handle_token,
            Commands.STORE: self._handle_store,
            Commands.RESTORE: self._handle_read,
            Commands.MAKEVP: self._handle_make_vp
        }

        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        return handlers[command](args)
