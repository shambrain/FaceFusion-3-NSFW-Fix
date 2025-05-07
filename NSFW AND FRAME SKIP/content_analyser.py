from functools import lru_cache
import cv2
import numpy
from typing import Any
from tqdm import tqdm

from facefusion import inference_manager, state_manager, wording
from facefusion.download import conditional_download_hashes, conditional_download_sources
from facefusion.filesystem import resolve_relative_path
from facefusion.thread_helper import conditional_thread_semaphore
from facefusion.vision import detect_video_fps, read_video_frame, read_image

PROBABILITY_LIMIT = 0.80
RATE_LIMIT = 10
STREAM_COUNTER = 0


@lru_cache(maxsize=None)
def create_static_model_set(download_scope: Any) -> dict:
    # NSFW model removed
    return {}


def get_inference_pool() -> dict:
    # Return empty inference pool since NSFW is removed
    return inference_manager.get_inference_pool(__name__, {})

  
def clear_inference_pool() -> None:
    # Since no NSFW models are used, we pass an empty list
    inference_manager.clear_inference_pool(__name__, [])


def get_model_options() -> dict:
    # No NSFW model options needed
    return {}


def pre_check() -> bool:
    # No NSFW model hashes to verify
    return True


def analyse_stream(vision_frame: Any, video_fps: int) -> bool:
    global STREAM_COUNTER
    STREAM_COUNTER += 1
    if STREAM_COUNTER % int(video_fps) == 0:
        return analyse_frame(vision_frame)
    return False


def analyse_frame(vision_frame: Any) -> bool:
    vision_frame = prepare_frame(vision_frame)
    probability = forward(vision_frame)
    return probability > PROBABILITY_LIMIT


def forward(vision_frame: Any) -> float:
    # Placeholder logic: always returns 0.0 since NSFW model is removed
    return 0.0


def prepare_frame(vision_frame: Any) -> Any:
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
                vision_frame = read_video_frame(video_path, frame_number)
                if analyse_frame(vision_frame):
                    counter += 1
            rate = counter * int(video_fps) / len(frame_range) * 100
            progress.update()
            progress.set_postfix(rate=rate)

    return rate > RATE_LIMIT
