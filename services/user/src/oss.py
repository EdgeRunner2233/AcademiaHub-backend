import tempfile
from obs import ObsClient
import src.config as config


class Obs_Client:
    """
    A class to interact with OBS
    """

    class ObsOperationError(Exception):
        """
        An error class for OBS
        """

    def __init__(self):
        self.obs_client = ObsClient(
            access_key_id=config.OBS_AK,
            secret_access_key=config.OBS_SK,
            server=config.OBS_SERVER,
        )

    def put_file(
        self, content: bytes, obs_filename: str, obs_dir=config.OBS_AVATAR_PREFIX
    ) -> str:
        """
        Upload a file to OBS

        Args:
            content (bytes): The content of the file to be uploaded
            obs_filename (str): The name of the file in OBS

        Raises:
            ObsOperationError: If the operation fails

        Returns:
            str: The URL of the uploaded file
        """

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content)
            res = self.obs_client.putFile(
                config.OBS_BUCKET_NAME, obs_dir + obs_filename, tmp.name
            )

        if res.status >= 300:
            raise Obs_Client.ObsOperationError(res.errorMessage)

        return config.OBS_BASE_URL + obs_dir + obs_filename

    def delete_file(self, obs_filename: str, obs_dir=config.OBS_AVATAR_PREFIX) -> bool:
        """
        Delete a file from OBS

        Args:
            obs_filename (str): The name of the file in OBS
            obs_dir (str, optional): The directory of the file in OBS. Defaults to config.OBS_AVATAR_PREFIX.

        Raises:
            ObsOperationError: If the operation fails

        Returns:
            bool: True if the file is deleted successfully, False otherwise
        """

        res = self.obs_client.deleteObject(
            config.OBS_BUCKET_NAME, obs_dir + obs_filename
        )

        if res.status >= 300:
            raise Obs_Client.ObsOperationError(res.errorMessage)

        return True


obs_client = Obs_Client()
