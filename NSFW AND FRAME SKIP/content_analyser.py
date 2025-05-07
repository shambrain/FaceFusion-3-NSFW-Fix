from functools import lru_cache
import cv2
import numpy
from typing import Any
from tqdm import tqdm

from facefusion import inference_manager, state_manager, wording
from facefusion.download import conditional_download_hashes, conditional_download_sources
from facefusion.filesystem import resolve_relative_path
from facefusion.thread_helper import conditional_thread_semaphore
from facefusion.vision import detect_video_fps, get_video_frame, read_image

# -----[ constants ]-----
PROBABILITY_LIMIT = 0.80
RATE_LIMIT = 10
STREAM_COUNTER = 0


@lru_cache(maxsize=None)
def create_static_model_set(download_scope: Any) -> dict:
    # NSFW model removed from pipeline
    return {}  # Empty model set


def get_inference_pool() -> dict:
    # No NSFW model is used anymore — returning empty inference pool
    return inference_manager.get_inference_pool(__name__, {})


def clear_inference_pool() -> None:
    inference_manager.clear_inference_pool(__name__)


def get_model_options() -> dict:
    # NSFW model options removed — not needed for inference now
    return {}


def pre_check() -> bool:
    # Skipping NSFW model hash/source checks — not needed
    return True


def analyse_stream(vision_frame: Any, video_fps: int) -> bool:
    global STREAM_COUNTER

    STREAM_COUNTER += 1
    if STREAM_COUNTER % int(video_fps) == 0:
        return analyse_frame(vision_frame)
    return False


def analyse_frame(vision_frame: Any) -> bool:
    vision_frame = prepare_frame(vision_frame)
    if vision_frame is None:
        return False  # Skip processing if frame was invalid

    # NSFW content analyzer removed — replaced with safe dummy logic
    probability = forward(vision_frame)
    return probability > PROBABILITY_LIMIT


def forward(vision_frame: Any) -> float:
    # Placeholder for future model logic
    return 0.0


def prepare_frame(vision_frame: Any) -> Any:
    if vision_frame is None or vision_frame.size == 0:
        # Skip invalid/empty frames
        return None

    model_size = get_model_options().get('size', (224, 224))
    model_mean = get_model_options().get('mean', [104, 117, 123])

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

    with tqdm(
        total=len(frame_range),
        desc=wording.get('analysing'),
        unit='frame',
        ascii=' =',
        disable=state_manager.get_item('log_level') in ['warn', 'error']
    ) as progress:
        for frame_number in frame_range:
            if frame_number % int(video_fps) == 0:
                vision_frame = get_video_frame(video_path, frame_number)

                if vision_frame is None or vision_frame.size == 0:
                    continue  # Skip invalid frames

                if analyse_frame(vision_frame):
                    counter += 1

            rate = counter * int(video_fps) / len(frame_range) * 100
            progress.update()
            progress.set_postfix(rate=rate)

    return rate > RATE_LIMIT
