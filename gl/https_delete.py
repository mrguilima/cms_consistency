
from rucio.client import Client
from rucio.common.exception import RucioException
import logging

def delete_remote_file_https(rse_name, scope, lfn, rucio_client):
    """
    Deletes a file from a remote Rucio Storage Element (RSE) using HTTPS.

    Args:
        rse_name (str): The name of the remote RSE.
        scope (str): The Rucio scope of the file.
        lfn (str): The Logical File Name (LFN) of the file.
        rucio_client (rucio.client.Client): An authenticated Rucio client.
    """
    try:
        # Construct the DID (Dataset Identifier)
        did = {'scope': scope, 'name': lfn}

        # Delete the file
        rucio_client.delete_dids([did], purge_replicas=True) # purge_replicas is important.
        logging.info(f"File {scope}:{lfn} deleted successfully from RSE {rse_name}.")

    except RucioException as e:
        logging.error(f"Failed to delete file {scope}:{lfn} from RSE {rse_name}: {e}")

def delete_remote_directory_https(rse_name, scope, lfn, rucio_client):
    """
    Deletes an empty directory from a remote Rucio Storage Element (RSE) using HTTPS.

    Args:
        rse_name (str): The name of the remote RSE.
        scope (str): The Rucio scope of the directory.
        lfn (str): The Logical File Name (LFN) of the directory.
        rucio_client (rucio.client.Client): An authenticated Rucio client.
    """
    try:
        did = {'scope': scope, 'name': lfn}
        rucio_client.delete_dids([did], purge_replicas=True)
        logging.info(f"Directory {scope}:{lfn} deleted successfully from RSE {rse_name}.")
    except RucioException as e:
        logging.error(f"Failed to delete directory {scope}:{lfn} from RSE {rse_name}: {e}")

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Rucio configuration (replace with your actual values)
    rucio_auth_type = 'x509_user_proxy' # or 'x509_user_cert' or 'oidc'
    rucio_account = 'your_account'
    rse_name = 'your_remote_rse' # The RSE name that supports HTTPS DELETE.
    scope = 'your_scope'
    file_lfn = 'your_file_to_delete.txt' # The LFN of the file to delete.
    directory_lfn = 'your_empty_directory' # The LFN of an empty directory to delete.

    # Create a Rucio client
    try:
        rucio_client = Client(auth_type=rucio_auth_type, account=rucio_account)
    except Exception as e:
        logging.error(f"Failed to create Rucio client: {e}")
        return

    # Delete a file
    delete_remote_file_https(rse_name, scope, file_lfn, rucio_client)

    # Delete an empty directory.
    delete_remote_directory_https(rse_name, scope, directory_lfn, rucio_client)

if __name__ == "__main__":
    main()
