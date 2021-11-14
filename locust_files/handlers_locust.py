import logging
import subprocess
from typing import List

from locust_files.interfaces_locust import Manager, Storage
from lvtool.helper import read_clue_file
from lvtool.types import Commands

logging.basicConfig(level=logging.INFO)


class Handler:
    def __init__(self, locust_client, phone_number):
        self.managers = {}
        self.storages = {}
        self._locust_client = locust_client
        self._phone_number = phone_number

        self._vpr_response = None
        self._vid_response = None
        self._token_response = None
        self._store_response = None

        make_clues_param = [
            'java', '-jar', 'LV-Client.jar', '-t', f'\"secret_for_{phone_number}\"', '-n', '3', '-th', '2', '-p', '1'
        ]

        call_out = subprocess.run(make_clues_param, stdout=subprocess.PIPE, check=False).stdout
        call_out = call_out.split(b'\n')
        self._clues = call_out[:3]
        self._secret = call_out[3]
        print(f"clues({self._clues}) secret({self._secret})")

    def get_manager(self, endpoint):
        if endpoint in self.managers:
            return self.managers[endpoint]
        self.managers[endpoint] = Manager(endpoint, self._locust_client)
        return self.managers[endpoint]

    def get_storage(self, storage_info):
        if storage_info['target'] in self.storages:
            return self.storages[storage_info['target']]
        self.storages[storage_info['target']] = Storage(storage_info, self._locust_client)
        return self.storages[storage_info['target']]

    def _handle_get_vp(self, args):
        manager = self.get_manager(endpoint=args.endpoint)
        logging.debug("- Requesting VPR...")
        vpr: dict = manager.request_vpr()  # TODO: THIS should contain VPRequest.
        logging.debug(f"- VPR Response: {vpr}")

        self._vpr_response = vpr

    def _handle_get_storages(self, args):
        manager = self.get_manager(endpoint=args.endpoint)
        logging.debug("- Requesting VID...")
        vp = None  # TODO: Make VP by VPR from lv-manager.

        # TODO: Fill VID Request according to responded VPR!
        vid_response = manager.issue_vid_request(phone_number=self._phone_number, vp=vp)
        logging.debug(f"- VID Response: {vid_response}")

        self._vid_response = vid_response

    def _handle_token(self, args):
        storages: List[dict] = []
        vID = self._vid_response["vID"]

        for storage_info in self._vid_response["storages"]:
            storage = self.get_storage(storage_info)
            storage.token_request(vID)
            storages.append(storage.to_json())

        self._token_response = {
            "vID": self._vid_response["vID"],
            "recovery_key": self._vid_response["recovery_key"],
            "storages": storages
        }

    def _handle_store(self, args):
        clues: List[str] = read_clue_file(args.clues)
        storages: List[dict] = []

        for clue, storage_info in zip(clues, self._vid_response["storages"]):
            storage = self.get_storage(storage_info)
            storage.store_request(clue)
            storages.append(storage.to_json())

        self._store_response = {
            "vID": self._vid_response["vID"],
            "recovery_key": self._vid_response["recovery_key"],
            "storages": storages
        }

    def _handle_read(self, args):
        storages = (self.get_storage(storage_info) for storage_info in self._vid_response["storages"])
        gathered_clues = []

        for storage in storages:
            response = storage.clue_request()
            gathered_clues.append(response["clue"])

        # with open(args.output, "w") as f:
        #     f.writelines("\n".join(gathered_clues))

    def __call__(self, command, args):
        handlers = {
            Commands.VPR: self._handle_get_vp,
            Commands.VID: self._handle_get_storages,
            Commands.TOKEN: self._handle_token,
            Commands.STORE: self._handle_store,
            Commands.RESTORE: self._handle_read,
        }

        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        return handlers[command](args)
