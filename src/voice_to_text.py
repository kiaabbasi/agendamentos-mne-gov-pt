from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError
import setings

def convert (path:str)-> str:
    """_summary_

    Args:
        path (str): path of the audio file

    Raises:
        KeyError: Invalid API key - Check your API_KEY at setting!
        ValueError: website error
        e: unexpected error

    Returns:
        str: the text extracted from file
    """
    API_KEY = setings.VOICE_TO_TXT_API_KEY
    LANGUAGE = "en"

    settings = ConnectionSettings(
        url="https://eu1.asr.api.speechmatics.com/v2",
        auth_token=API_KEY,
    )

    # Define transcription parameters
    conf = {"type": "transcription", "transcription_config": {"language": LANGUAGE, "operating_point": "enhanced"}}

    # Open the client using a context manager
    with BatchClient(settings) as client:
        try:
            job_id = client.submit_job(
                audio=path,
                transcription_config=conf,
            )
            
            # Note that in production, you should set up notifications instead of polling.
            # Notifications are described here: https://docs.speechmatics.com/speech-to-text/batch/notifications
            transcript = client.wait_for_completion(job_id, transcription_format="txt")
            # To see the full output, try setting transcription_format='json-v2'.
            return str(transcript)
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                raise KeyError ("Invalid API key - Check your API_KEY at the top of the code!")
            elif e.response.status_code == 400:
                raise ValueError (e.response.json()["detail"])
            else:
                raise e
            