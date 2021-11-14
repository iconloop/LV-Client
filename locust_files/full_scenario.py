import random

import time
from locust import HttpUser, task, between, events

from locust_files.handlers_locust import Handler, Failure
from lvtool.parsers import init_parsers

TEST_TIMEOUT = 500  # millisecond


class LiteVaultClient(HttpUser):
    wait_time = between(1, 2.5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phone_number_for_vid = f"010{random.randrange(10000000, 99999999)}"
        self.lv_handler = Handler(self.client, phone_number_for_vid)
        self.parser = init_parsers()

    @task(1)
    def vpr(self):
        """Get VPR

        :return:
        """
        self.lv_handler(
            'vpr',
            self.parser.parse_args(['vpr', '-e', 'lv-manager.iconscare.com', '-o', 'vpr.json']))

    @task(1)
    def vid(self):
        """Get Storages

        :return:
        """
        self.lv_handler(
            'vid',
            self.parser.parse_args(['vid', '-e', 'lv-manager.iconscare.com', '-f', 'vpr.json', '-o', 'storages.json']))

    @task(2)
    def token(self):
        """Get Tokens from Storages

        :return:
        """
        self.lv_handler(
            'token',
            self.parser.parse_args(['token', '-f', 'storages.json', '-o', 'tokens.json']))

    @task(6)
    def store(self):
        """Store clues to Storages

        :return:
        """
        start_time = time.time()

        self.lv_handler(
            'store',
            self.parser.parse_args(['store', 'clues', '-f', 'tokens.json', '-o', 'store_output.json']))

        total_time = int((time.time() - start_time) * 1000)

        if total_time > TEST_TIMEOUT:
            events.request_failure.fire(
                request_type="POST", name="STORE_0", response_time=total_time, response_length=0,
                exception=Failure('Test timeout')
            )

    @task(3)
    def read(self):
        """Read clues from Storages

        :return:
        """
        start_time = time.time()

        self.lv_handler(
            'read',
            self.parser.parse_args(['read', '-f', 'store_output.json', '-o', 'restored_clues.txt'])
        )

        total_time = int((time.time() - start_time) * 1000)

        if total_time > TEST_TIMEOUT:
            events.request_failure.fire(
                request_type="POST", name="CLUE_0", response_time=total_time, response_length=0,
                exception=Failure('Test timeout')
            )

    def on_start(self):
        """Prepare files"""
        self.lv_handler(
            'vpr',
            self.parser.parse_args(['vpr', '-e', 'lv-manager.iconscare.com', '-o', 'vpr.json']))
        self.lv_handler(
            'vid',
            self.parser.parse_args(['vid', '-e', 'lv-manager.iconscare.com', '-f', 'vpr.json', '-o', 'storages.json']))
        self.lv_handler(
            'token',
            self.parser.parse_args(['token', '-f', 'storages.json', '-o', 'tokens.json']))
        self.lv_handler(
            'store',
            self.parser.parse_args(['store', 'clues', '-f', 'tokens.json', '-o', 'store_output.json']))
        self.lv_handler(
            'read',
            self.parser.parse_args(['read', '-f', 'store_output.json', '-o', 'restored_clues.txt']))
