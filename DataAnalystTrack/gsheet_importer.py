import pandas as pd
from pathlib import Path
from gspread_pandas import Spread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsAdapter:
    """Simple wrapper over the gspread_pandas library to read Google sheets as Pandas
    Dataframes.
​
    The service_client_secret.json file contains the credentials required to interact
    with the Google spreadsheet. You can obtain this file by contacting any of the
    contributors to this repo or contact David Elliot or Hugo Darwood. Hopefully, at
    some point, there'll be a more future proof way to share these credentials
​
    Parameters
    ----------
    document_id : str
        name, url, or id of the spreadsheet; must have read access by
        the authenticated user,
    path_to_client_secret : str, optional
        path to the json file containing the credential information for the user to be
        authenticated to read the Google Sheet. If not provided then it will try to look
        for the file in a default location.
    """

    DEFAULT_SECRET_PATH = Path.home() / "Projects/Pandas/deliveroo-docs-api.json"

    def __init__(self, document_id: str, path_to_client_secret: str = None) -> None:
        if path_to_client_secret:
            filepath_to_secrets = Path(path_to_client_secret)
        else:
            filepath_to_secrets = self.DEFAULT_SECRET_PATH
        credentials = self._get_credentials(filepath_to_secrets)
        self.spread_obj = Spread(spread=document_id, creds=credentials)

    def get_gsheet(self, sheet_name: str, **kwargs) -> pd.DataFrame:
        """Extract the Google sheet data

        This method takes the name of the sheet and extracts the data as a Pandas
        DataFrame
​
        Parameters
        ----------
        sheet_name : str
            name of the spreadsheet that you want to extract
        kwargs : dict, optional
            Keyword arguments that go into the `sheet_to_df` method in the Spread
            object. See the following link for details
            https://github.com/aiguofer/gspread-pandas/blob/master/gspread_pandas/spread.py#L354
​
        Returns
        -------
        DataFrame
            DataFrame with the data from the Worksheet
    """
        return self.spread_obj.sheet_to_df(sheet=sheet_name, **kwargs)

    def _get_credentials(
        self, path_to_client_secret: Path
    ) -> ServiceAccountCredentials:
        """Get credentials required for authentication
​
        Parameters
        ----------
        path_to_client_secret : pathlib.Path
            path object to the json file containing the credential information for the
            user to be authenticated to read the Google Sheet.
​
        Returns
        -------
        ServiceAccountCredentials
            Credentials required to authenticate user
        """
        if path_to_client_secret.exists():
            return ServiceAccountCredentials.from_json_keyfile_name(
                path_to_client_secret, SCOPES
            )
        else:
            raise ValueError(f"Credentials file: '{path_to_client_secret}' not found")


if __name__ == "__main__":
    gs_id_labels = "1aLUMR66VztKwKFzSoGUuavb0td408HvEzvHkpC80Swg"
    gsheet = GoogleSheetsAdapter(document_id=gs_id_labels)
    data_frame_1 = gsheet.get_gsheet("Sheet1")
    data_frame_2 = gsheet.get_gsheet("sxversion", index=0)
    print(data_frame_1)
