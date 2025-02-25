from functools import lru_cache

import cv2
import numpy
from tqdm import tqdm

from facefusion import inference_manager, state_manager, wording
from facefusion.download import conditional_download_hashes, conditional_download_sources, resolve_download_url
from facefusion.filesystem import resolve_relative_path
from facefusion.thread_helper import conditional_thread_semaphore
from facefusion.typing import DownloadScope, Fps, InferencePool, ModelOptions, ModelSet, VisionFrame
from facefusion.vision import detect_video_fps, get_video_frame, read_image

PROBABILITY_LIMIT = 0.80
RATE_LIMIT = 10
STREAM_COUNTER = 0


@lru_cache(maxsize=None)
def create_static_model_set(download_scope: DownloadScope) -> ModelSet:
    # Removed 'open_nsfw' model and related data
    # Keeping track of the removal to avoid potential future re-implementation
    return {}


def get_inference_pool() -> InferencePool:
    # Return an empty pool as we no longer have the NSFW model
    return inference_manager.get_inference_pool(__name__, {})


def clear_inference_pool() -> None:
    inference_manager.clear_inference_pool(__name__)


def get_model_options() -> ModelOptions:
    # Return an empty dictionary as we no longer need model options for NSFW
    return {}


def pre_check() -> bool:
    # No need to check for NSFW model hashes or sources
    return True


def analyse_stream(vision_frame: VisionFrame, video_fps: Fps) -> bool:
    global STREAM_COUNTER

    STREAM_COUNTER = STREAM_COUNTER + 1
    if STREAM_COUNTER % int(video_fps) == 0:
        return analyse_frame(vision_frame)
    return False


def analyse_frame(vision_frame: VisionFrame) -> bool:
    vision_frame = prepare_frame(vision_frame)
    # Removed the NSFW content analyzer call (as part of our change)
    # The frame will now proceed with the modified logic
    probability = forward(vision_frame)

    return probability > PROBABILITY_LIMIT


def forward(vision_frame: VisionFrame) -> float:
    # Removed the NSFW content analyzer call
    # Placeholder function for future inference (may be replaced with other tasks)
    return 0.0  # Placeholder for now; modify as needed


def prepare_frame(vision_frame: VisionFrame) -> VisionFrame:
    # Check if vision_frame is empty
    if vision_frame is None or vision_frame.size == 0:
        # Instead of throwing an error, we skip the frame if it's empty
        # This ensures we don't process invalid or empty frames which might crash the application
        return None  # This will trigger the frame skip in the analysis pipeline
        
    # Continue with the resize if frame is valid
    model_size = get_model_options().get('size', (224, 224))  # Default size if model size isn't specified
    model_mean = get_model_options().get('mean', [104, 117, 123])  # Default mean if not specified
    
    # Resize and preprocess the frame
    vision_frame = cv2.resize(vision_frame, model_size).astype(numpy.float32)
    vision_frame -= numpy.array(model_mean).astype(numpy.float32)
    vision_frame = numpy.expand_dims(vision_frame, axis=0)
    return vision_frame


@lru_cache(maxsize=None)
def analyse_image(image_path: str) -> bool:
    vision_frame = read_image(image_path)
    return analyse_frame(vision_frame)


@lru_cache(maxsize=None)
def analyse_video(video_path: str, trim_frame_start: int, trim_frame_end: int) -> bool:
    video_fps = detect_video_fps(video_path)
    frame_range = range(trim_frame_start, trim_frame_end)
    rate = 0.0
    counter = 0

    with tqdm(total=len(frame_range), desc=wording.get('analysing'), unit='frame', ascii=' =', disable=state_manager.get_item('log_level') in ['warn', 'error']) as progress:
        for frame_number in frame_range:
            if frame_number % int(video_fps) == 0:
                vision_frame = get_video_frame(video_path, frame_number)

                # # New Frame Skipping Logic (added change here)
                # Skip invalid or empty frames (added as part of the frame skipping feature)
                if vision_frame is None or vision_frame.size == 0:
                    # Instead of throwing an error, simply continue the loop (frame is skipped)
                    continue  # Skipping frames that failed to load

                if analyse_frame(vision_frame):
                    counter += 1

            rate = counter * int(video_fps) / len(frame_range) * 100
            progress.update()
            progress.set_postfix(rate=rate)

    return rate > RATE_LIMIT
