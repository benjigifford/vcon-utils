import requests
import hashlib
import base64
from datetime import datetime
from typing import Optional, List, Dict, Union, Any, Tuple
from .party import PartyHistory
from dateutil import parser

MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/webm",
    "audio/x-m4a",
    "audio/aac",
    # Existing video types
    "video/x-mp4",
    "video/ogg",
    # New video types
    "video/mp4",              # MP4 format
    "video/quicktime",        # MOV format
    "video/webm",             # WebM format
    "video/x-msvideo",        # AVI format
    "video/x-matroska",       # MKV format
    "video/mpeg",             # MPEG format
    "video/x-flv",            # FLV format
    "video/3gpp",             # 3GP format for mobile
    "video/x-m4v",            # M4V format (Apple variant)
    "multipart/mixed",
    "message/rfc822",
    "application/json"        # For signaling data
]


class Dialog:
    # Updated MIME_TYPES list with comprehensive video format support
    MIME_TYPES = [
        "text/plain",
        "audio/x-wav",
        "audio/wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/ogg",
        "audio/webm",
        "audio/x-m4a",
        "audio/aac",
        # Existing video types
        "video/x-mp4",
        "video/ogg",
        # New video types with comprehensive format support
        "video/mp4",              # MP4 format
        "video/quicktime",        # MOV format
        "video/webm",             # WebM format
        "video/x-msvideo",        # AVI format
        "video/x-matroska",       # MKV format
        "video/mpeg",             # MPEG format
        "video/x-flv",            # FLV format
        "video/3gpp",             # 3GP format for mobile
        "video/x-m4v",            # M4V format (Apple variant)
        "multipart/mixed",
        "message/rfc822",
        "application/json"        # For signaling data
    ]

    # Add "video" to the list of valid types if not already present
    VALID_TYPES = [
        "recording", 
        "text", 
        "transfer", 
        "incomplete",
        "audio",
        "video"
    ]

    def __init__(
        self,
        type: str,
        start: Union[datetime, str],
        parties: List[int],
        originator: Optional[int] = None,
        mimetype: Optional[str] = None,
        filename: Optional[str] = None,
        body: Optional[str] = None,
        encoding: Optional[str] = None,
        url: Optional[str] = None,
        alg: Optional[str] = None,
        signature: Optional[str] = None,
        disposition: Optional[str] = None,
        party_history: Optional[List[PartyHistory]] = None,
        transferee: Optional[int] = None,
        transferor: Optional[int] = None,
        transfer_target: Optional[int] = None,
        original: Optional[int] = None,
        consultation: Optional[int] = None,
        target_dialog: Optional[int] = None,
        campaign: Optional[str] = None,
        interaction: Optional[str] = None,
        skill: Optional[str] = None,
        duration: Optional[float] = None,
        meta: Optional[dict] = None,
        # New parameters for signaling and extended functionality
        metadata: Optional[Dict[str, Any]] = None,
        transfer: Optional[Dict[str, Any]] = None,
        signaling: Optional[Dict[str, Any]] = None,
        # New parameters for video metadata
        resolution: Optional[str] = None,
        frame_rate: Optional[float] = None,
        codec: Optional[str] = None,
        bitrate: Optional[int] = None,
        thumbnail: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a Dialog object.
        :param type: the type of the dialog (e.g. "text", "recording", "transfer", "incomplete", "video")
        :type type: str
        :param start: the start time of the dialog
        :type start: datetime
        :param parties: the parties involved in the dialog
        :type parties: List[int]
        :param originator: the party that originated the dialog
        :type originator: int or None
        :param mimetype: the MIME type of the dialog body
        :type mimetype: str or None
        :param filename: the filename of the dialog body
        :type filename: str or None
        :param body: the body of the dialog
        :type body: str or None
        :param encoding: the encoding of the dialog body
        :type encoding: str or None
        :param url: the URL of the dialog
        :type url: str or None
        :param alg: the algorithm used to sign the dialog
        :type alg: str or None
        :param signature: the signature of the dialog
        :type signature: str or None
        :param disposition: the disposition of the dialog
        :type disposition: str or None
        :param party_history: the history of parties involved in the dialog
        :type party_history: List[PartyHistory] or None
        :param transferee: the party that the dialog was transferred to
        :type transferee: int or None
        :param transferor: the party that transferred the dialog
        :type transferor: int or None
        :param transfer_target: the target of the transfer
        :type transfer_target: int or None
        :param original: the original dialog
        :type original: int or None
        :param consultation: the consultation dialog
        :type consultation: int or None
        :param target_dialog: the target dialog
        :type target_dialog: int or None
        :param campaign: the campaign that the dialog is associated with
        :type campaign: str or None
        :param interaction: the interaction that the dialog is associated with
        :type interaction: str or None
        :param skill: the skill that the dialog is associated with
        :type skill: str or None
        :param duration: the duration of the dialog
        :type duration: float or None
        :param meta: additional metadata for the dialog
        :type meta: dict or None
        :param metadata: structured metadata for the dialog (newer format)
        :type metadata: dict or None
        :param transfer: transfer-specific information
        :type transfer: dict or None
        :param signaling: signaling-specific information
        :type signaling: dict or None
        :param resolution: video resolution (e.g., "1920x1080")
        :type resolution: str or None
        :param frame_rate: video frame rate in fps
        :type frame_rate: float or None
        :param codec: video codec (e.g., "H.264", "H.265")
        :type codec: str or None
        :param bitrate: video bitrate in kbps
        :type bitrate: int or None
        :param thumbnail: base64-encoded thumbnail image
        :type thumbnail: str or None
        :param kwargs: Additional attributes to be set on the dialog
        """

        # Validate dialog type
        if type not in self.VALID_TYPES:
            raise ValueError(f"Invalid dialog type: {type}. Must be one of {self.VALID_TYPES}")

        # Convert the start time to an ISO 8601 string from a datetime or a string
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, str):
            start = parser.parse(start).isoformat()
            
        # Set attributes from named parameters that are not None
        for key, value in locals().items():
            if value is not None and key not in ("self", "kwargs"):
                setattr(self, key, value)

        # Don't merge meta and metadata; keep both for backward compatibility
        # This ensures tests relying on dialog.meta will continue to work
        # while also allowing new code to use dialog.metadata
        if not hasattr(self, "metadata") and hasattr(self, "meta"):
            self.metadata = self.meta.copy() if self.meta else {}
        elif not hasattr(self, "meta") and hasattr(self, "metadata"):
            self.meta = self.metadata.copy() if self.metadata else {}
        elif not hasattr(self, "metadata") and not hasattr(self, "meta"):
            self.metadata = {}
            self.meta = {}

        # Set any additional kwargs as attributes
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        # Handling for specific dialog types
        if type == "incomplete" and not hasattr(self, "disposition"):
            raise ValueError("Dialog type 'incomplete' requires a disposition")
            
        # Auto-detect mimetype for video type
        if type == "video" and not hasattr(self, "mimetype"):
            # Try to infer mimetype from filename extension if available
            if hasattr(self, "filename") and self.filename:
                ext = self.filename.split('.')[-1].lower()
                if ext == "mp4":
                    self.mimetype = "video/mp4"
                elif ext == "mov":
                    self.mimetype = "video/quicktime"
                elif ext == "webm":
                    self.mimetype = "video/webm"
                elif ext == "avi":
                    self.mimetype = "video/x-msvideo"
                elif ext == "mkv":
                    self.mimetype = "video/x-matroska"
                elif ext in ["mpg", "mpeg"]:
                    self.mimetype = "video/mpeg"
                elif ext == "flv":
                    self.mimetype = "video/x-flv"
                elif ext == "3gp":
                    self.mimetype = "video/3gpp"
                elif ext == "m4v":
                    self.mimetype = "video/x-m4v"
                else:
                    # Default to MP4 if we can't determine from extension
                    self.mimetype = "video/mp4"
            else:
                # Default mimetype for video
                self.mimetype = "video/mp4"

    def to_dict(self):
        """
        Returns a dictionary representation of the Dialog object.

        :return: a dictionary containing all non-None Dialog object attributes
        :rtype: dict
        """
        # Check to see if the start time provided. If not,
        # set the start time to the current time
        if not hasattr(self, "start"):
            self.start = datetime.now().isoformat()

        # Get all attributes of the object
        dialog_dict = self.__dict__.copy()

        # Handle party_history specially
        if hasattr(self, "party_history") and self.party_history:
            dialog_dict["party_history"] = [
                party_history.to_dict() for party_history in self.party_history
            ]

        return {k: v for k, v in dialog_dict.items() if v is not None}

    def add_external_data(self, url: str, filename: str = None, mimetype: str = None) -> None:
        """
        Add external data to the dialog.

        :param url: the URL of the external data
        :type url: str
        :param filename: the filename to use (optional)
        :type filename: str or None
        :param mimetype: the mimetype to use (optional)
        :type mimetype: str or None
        :return: None
        :rtype: None
        """
        self.url = url
        
        # Make a HEAD request to get metadata without downloading the content
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type")
            content_length = response.headers.get("Content-Length")
            
            # Override content type if mimetype provided
            if mimetype:
                self.mimetype = mimetype
            else:
                self.mimetype = content_type
                
            # Override filename if provided, otherwise extract from URL
            if filename:
                self.filename = filename
            else:
                # Extract filename from URL, removing any query parameters
                url_path = url.split("?")[0]
                self.filename = url_path.split("/")[-1]
                
            # Calculate a signature without downloading the full content
            self.alg = "external-reference"
            self.encoding = "none"
            
            # Store additional metadata for videos
            if self.is_video():
                # If content length is available, store it in metadata
                if content_length:
                    if not hasattr(self, "metadata"):
                        self.metadata = {}
                    self.metadata["content_length"] = int(content_length)
        else:
            raise Exception(f"Failed to fetch external data metadata: {response.status_code}")

    def add_inline_data(self, body: str, filename: str, mimetype: str) -> None:
        """
        Add inline data to the dialog.

        :param body: the body of the inline data
        :type body: str
        :param filename: the filename of the inline data
        :type filename: str
        :param mimetype: the mimetype of the inline data
        :type mimetype: str
        :return: None
        :rtype: None
        """
        self.body = body
        self.mimetype = mimetype
        self.filename = filename
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(self.body.encode()).digest()
        ).decode()

    def add_video_data(self, source: str, metadata: Dict[str, Any] = None, is_external: bool = True, **kwargs) -> None:
        """
        Add video data to the dialog with extended metadata.
        
        :param source: URL or base64-encoded video data
        :type source: str
        :param metadata: Additional video metadata
        :type metadata: Dict[str, Any] or None
        :param is_external: Whether the source is an external URL (True) or inline data (False)
        :type is_external: bool
        :param kwargs: Additional video attributes (resolution, codec, frame_rate, etc.)
        :return: None
        :rtype: None
        """
        # Set dialog type to video
        self.type = "video"
        
        # Initialize metadata if not provided
        if not hasattr(self, "metadata") or self.metadata is None:
            self.metadata = {}
            
        # Initialize meta if not present
        if not hasattr(self, "meta") or self.meta is None:
            self.meta = {}
            
        # Update metadata with provided values
        if metadata:
            self.metadata.update(metadata)
            self.meta.update(metadata)  # Update both for backward compatibility
            
        # Extract filename from source if it's a URL
        filename = kwargs.get("filename")
        if is_external and not filename:
            url_path = source.split("?")[0]
            filename = url_path.split("/")[-1]
            
        # Determine mimetype if not provided
        mimetype = kwargs.get("mimetype")
        if not mimetype and filename:
            ext = filename.split('.')[-1].lower()
            if ext == "mp4":
                mimetype = "video/mp4"
            elif ext == "mov":
                mimetype = "video/quicktime"
            elif ext == "webm":
                mimetype = "video/webm"
            elif ext == "avi":
                mimetype = "video/x-msvideo"
            elif ext == "mkv":
                mimetype = "video/x-matroska"
            elif ext in ["mpg", "mpeg"]:
                mimetype = "video/mpeg"
            elif ext == "flv":
                mimetype = "video/x-flv"
            elif ext == "3gp":
                mimetype = "video/3gpp"
            elif ext == "m4v":
                mimetype = "video/x-m4v"
            else:
                # Default to MP4 if we can't determine from extension
                mimetype = "video/mp4"
                
        # Add video data (external or inline)
        if is_external:
            self.add_external_data(source, filename, mimetype)
        else:
            self.add_inline_data(source, filename, mimetype)
            
        # Set additional video attributes from kwargs
        for key, value in kwargs.items():
            if key not in ["filename", "mimetype"] and value is not None:
                setattr(self, key, value)
                
    def extract_video_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the video dialog.
        
        This is a placeholder method that would typically use a library like FFmpeg
        to extract metadata from the video. In a real implementation, this would
        connect to external tools to analyze the video content.
        
        :return: Dictionary containing extracted video metadata
        :rtype: Dict[str, Any]
        """
        # In a real implementation, this would use FFmpeg or similar tools
        # to extract metadata from the video content
        
        # Return metadata that's already stored
        result = {}
        
        # Include basic metadata that we might already have
        for field in ["resolution", "frame_rate", "codec", "bitrate", "duration"]:
            if hasattr(self, field):
                result[field] = getattr(self, field)
                
        # Include any additional metadata
        if hasattr(self, "metadata"):
            result.update(self.metadata)
            
        return result
    
    def generate_thumbnail(self, timestamp: float = None) -> str:
        """
        Generate a thumbnail from the video at the specified timestamp.
        
        This is a placeholder method that would typically use a library like FFmpeg
        to generate a thumbnail. In a real implementation, this would extract a frame
        from the video and return it as a base64-encoded image.
        
        :param timestamp: Time in seconds to extract thumbnail (defaults to 10% of duration)
        :type timestamp: float or None
        :return: Base64-encoded thumbnail image
        :rtype: str
        """
        # In a real implementation, this would use FFmpeg to extract a frame
        # from the video at the specified timestamp
        
        # If we already have a thumbnail, return it
        if hasattr(self, "thumbnail"):
            return self.thumbnail
            
        # Placeholder: In a real implementation, this would generate and return a thumbnail
        return "Generated thumbnail would be returned here"
        
    def update_video_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update the video metadata.
        
        :param metadata: New metadata to add or update
        :type metadata: Dict[str, Any]
        :return: None
        :rtype: None
        """
        if not hasattr(self, "metadata"):
            self.metadata = {}
            
        if not hasattr(self, "meta"):
            self.meta = {}
            
        # Update both metadata and meta for backward compatibility
        self.metadata.update(metadata)
        self.meta.update(metadata)
        
        # Also set direct attributes for key metadata fields
        for key, value in metadata.items():
            if key in ["resolution", "frame_rate", "codec", "bitrate", "duration", "thumbnail"]:
                setattr(self, key, value)

    def is_external_data(self) -> bool:
        """
        Check if the dialog is an external data dialog.

        :return: True if the dialog is an external data dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "url")

    def is_inline_data(self) -> bool:
        """
        Check if the dialog is an inline data dialog.

        :return: True if the dialog is an inline data dialog, False otherwise
        :rtype: bool
        """
        return not self.is_external_data()

    def is_text(self) -> bool:
        """
        Check if the dialog is a text dialog.
        :return: True if the dialog is a text dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "text"
    
    def is_recording(self) -> bool:
        """
        Check if the dialog is a recording dialog.
        :return: True if the dialog is a recording dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "recording"
    
    def is_transfer(self) -> bool:
        """
        Check if the dialog is a transfer dialog.
        :return: True if the dialog is a transfer dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "transfer"
    
    def is_incomplete(self) -> bool:
        """
        Check if the dialog is an incomplete dialog.
        :return: True if the dialog is an incomplete dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "incomplete"
    
    def is_audio(self) -> bool:
        """
        Check if the dialog has audio content.
        :return: True if the dialog has audio content, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype in [
            "audio/x-wav",
            "audio/wav",
            "audio/wave",
            "audio/mpeg",
            "audio/mp3",
            "audio/ogg",
            "audio/webm",
            "audio/x-m4a",
            "audio/aac",
        ]
    
    def is_video(self) -> bool:
        """
        Check if the dialog has video content.
        :return: True if the dialog has video content, False otherwise
        :rtype: bool
        """
        # Check if the dialog type is explicitly "video"
        type_is_video = hasattr(self, "type") and self.type == "video"
        
        # Check if the mimetype indicates video content
        mimetype_is_video = hasattr(self, "mimetype") and self.mimetype in [
            # Existing video formats
            "video/x-mp4",
            "video/ogg",
            # New video formats
            "video/mp4",
            "video/quicktime",
            "video/webm",
            "video/x-msvideo",
            "video/x-matroska",
            "video/mpeg",
            "video/x-flv",
            "video/3gpp",
            "video/x-m4v"
        ]
        
        return type_is_video or mimetype_is_video
    
    def is_email(self) -> bool:
        """
        Check if the dialog is an email dialog.
        :return: True if the dialog is an email dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype == "message/rfc822"
    
    def is_external_data_changed(self) -> bool:
        """
        Check to see if it's an external data dialog, that the contents are valid by
        checking the hash of the body against the signature.

        :return: True if the dialog is an external data dialog and the contents are valid, False otherwise
        :rtype: bool
        """
        if not self.is_external_data():
            return False
        try:
            body_hash = base64.urlsafe_b64decode(self.signature.encode())
            return hashlib.sha256(self.body.encode()).digest() != body_hash
        except Exception as e:
            print(e)
            return True

    # Convert the dialog from an external data dialog to an inline data dialog
    # by reading the contents from the URL then adding the contents to the body
    def to_inline_data(self) -> None:
        """
        Convert the dialog from an external data dialog to an inline data dialog
        by reading the contents from the URL then adding the contents to the body.

        :return: None
        :rtype: None
        """
        if not self.is_external_data():
            return  # Already inline, nothing to do
            
        # Read the contents from the URL
        response = requests.get(self.url)
        if response.status_code == 200:
            # For binary content, use response.content instead of response.text
            raw_content = response.content
            
            # Handle different encoding based on content type
            if self.is_video() or self.is_audio():
                # For binary media content, use base64url encoding
                self.body = base64.urlsafe_b64encode(raw_content).decode()
                self.encoding = "base64url"
            else:
                # For text content, try to encode as UTF-8
                try:
                    self.body = raw_content.decode('utf-8')
                    self.encoding = "none"
                except UnicodeDecodeError:
                    # If not decodable as text, use base64url
                    self.body = base64.urlsafe_b64encode(raw_content).decode()
                    self.encoding = "base64url"
                    
            # Update mimetype if not already set
            if not hasattr(self, "mimetype") or not self.mimetype:
                self.mimetype = response.headers.get("Content-Type")
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Calculate the SHA-256 hash of the original binary content
        self.alg = "sha256"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(raw_content).digest()
        ).decode()

        # Set the filename if it doesn't exist
        if not hasattr(self, "filename"):
            self.filename = self.url.split("/")[-1]

        # Remove the url since this is now inline data
        delattr(self, "url")
        
        # For video content, try to extract additional metadata
        if self.is_video():
            # In a real implementation, this would use FFmpeg to extract metadata
            # like duration, resolution, etc.
            pass
