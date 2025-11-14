# to generate Agora RTC tokens and get help with it too
from typing import Optional
import time


def generate_rtc_token(app_id: str, app_certificate: str, channel: str, uid: Optional[int] = 0, role: int = 1, expire_seconds: int = 3600) -> str:
    """Generate an RTC token using the Agora token builder package.

    Parameters:
    - app_id: Agora App ID
    - app_certificate: Agora App Certificate (secret)
    - channel: channel name
    - uid: numeric uid (0 means random if you prefer)
    - role: 1 = publisher/host (in some builders it's role: rtc Role)
    - expire_seconds: token TTL in seconds

    Returns: token string
    """
    try:
        # The common token builder module name
        from agora_token_builder import RtcTokenBuilder
    except Exception as e:
        raise RuntimeError(
            "Agora token builder package not installed. Run: pip install agora-access-token\n" \
            "or install the appropriate agora token builder package for your environment.\n" \
            "Original error: " + str(e)
        )

    current_ts = int(time.time())
    privilege_expired_ts = current_ts + int(expire_seconds)
    # RtcTokenBuilder.buildTokenWithUid takes role value from the builder; common usage sets role=1 for publisher
    token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel, uid, role, privilege_expired_ts)
    return token


if __name__ == '__main__':
    import os
    APP_ID = os.environ.get('AGORA_APP_ID')
    APP_CERT = os.environ.get('AGORA_APP_CERT')
    if not APP_ID or not APP_CERT:
        print('Set AGORA_APP_ID and AGORA_APP_CERT in env to generate a token')
    else:
        print(generate_rtc_token(APP_ID, APP_CERT, 'testchannel', uid=0, expire_seconds=3600))
