from vaultwarden.models.bitwarden import BitwardenAPIClient
from vaultwarden.models.bitwarden import get_organization
from vaultwarden.utils.crypto import decrypt
from app.config.config import config
from app.utils.log import output_log
from pydantic.dataclasses import dataclass


@dataclass
class BitwardenData:
    name: str
    password: str = ""
    username: str = ""
    url: str | None = None
    notes: str | None = None


class BitwardenClient:
    def __init__(
        self,
        url: str = config.vaultwarden_host,
        email: str = config.vaultwarden_email,
        password: str = config.vaultwarden_password,
        client_id: str = config.vaultwarden_client_id,
        client_secret: str = config.vaultwarden_client_secret,
        device_id: str = "python",
        org_id: str = config.vaultwarden_org_id,
    ):
        self.url = url
        self.email = email
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_id = device_id
        self.org_id = org_id
        self._set_up()

    @property
    def get_client(self):
        return self._client

    @property
    def get_organization(self):
        return self._organization

    @property
    def get_collections(self):
        return self._collections

    def _set_up(self):
        self._client = BitwardenAPIClient(
            url=self.url,
            email=self.email,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
            device_id=self.device_id,
        )
        output_log(
            f"Connect to Bitwarden with config: {self.url}, {self.email}, {self.client_id}, {self.device_id}",
            "debug",
        )
        try:
            self._organization = get_organization(self._client, self.org_id)
            self._collections = self._organization.collections(as_dict=True)
        except Exception as e:
            output_log(f"Error connecting to Bitwarden: {e} for {self.org_id}", "error")
            raise e

    def get_ciphers(self, collection_id) -> list[BitwardenData]:
        ciphers = self._organization.ciphers(
            self._collections.get(collection_id).Id, force_refresh=True
        )
        result = []
        for cipher in ciphers:
            try:
                name = cipher.Name if cipher.Name else ""
                notes = self._filed_decrypt(cipher.notes if cipher.notes else "")
                if cipher.login is not None:
                    password = self._filed_decrypt(cipher.login.get("password", ""))
                    username = self._filed_decrypt(cipher.login.get("username", ""))
                    url = self._filed_decrypt(cipher.login.get("uri", ""))
                else:
                    password = ""
                    username = ""
                    url = ""
                result.append(
                    BitwardenData(
                        name=name,
                        password=password,
                        username=username,
                        url=url,
                        notes=notes,
                    )
                )
            except Exception as e:
                output_log(f"Error decrypting cipher data: {e} for cipher", "error")
                continue
        return result

    def _filed_decrypt(self, field):
        if field is None or field == "":
            return ""
        return decrypt(field, self._organization.key()).decode("utf-8")
