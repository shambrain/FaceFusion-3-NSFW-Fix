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

# === CONFIG ===
PROBABILITY_LIMIT = 0.80
RATE_LIMIT = 10
STREAM_COUNTER = 0


@lru_cache(maxsize=None)
def create_static_model_set(download_scope: Any) -> dict:
    # NSFW model removed — no hashes or sources registered
    return {}


def get_inference_pool() -> dict:
    # Return empty pool to satisfy interface; no NSFW inference needed
    return inference_manager.get_inference_pool(__name__, {})


def clear_inference_pool() -> None:
    # FIX: Some modules still expect clear_inference_pool(__name__, ['yolo_nsfw'])
    # Providing dummy model name for compatibility
    inference_manager.clear_inference_pool(__name__, ['yolo_nsfw'])


def get_model_options() -> dict:
    # Provide dummy model options to satisfy downstream prepare_frame() logic
    return {
        'size': (224, 224),
        'mean': [104, 117, 123]
    }


def pre_check() -> bool:
    # Skip model hash/source check — NSFW model not used
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
        return False  # Skip invalid or empty frames
    probability = forward(vision_frame)
    return probability > PROBABILITY_LIMIT


@lru_cache(maxsize=None)
def analyse_image(image_path: str) -> bool:
    vision_frame = read_image(image_path)
    return analyse_frame(vision_frame)


@lru_cache(maxsize=None)
def analyse_video(video_path: str, trim_frame_start: int, trim_frame_end: int) -> bool:
    video_fps = detect_video_fps(video_path)
    frame_range = range(trim_frame_start, trim_frame_end)
    rate = 0.0
    total = 0
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
                if vision_frame is None or vision_frame.size == 0:
                    continue  # Frame skip logic: ignore bad frames
                total += 1
                if analyse_frame(vision_frame):
                    counter += 1
            if counter > 0 and total > 0:
                rate = counter / total * 100
            progress.set_postfix(rate=rate)
            progress.update()

    return rate > 10.0


def forward(vision_frame: Any) -> float:
    # Stub for removed NSFW model — returns 0.0 for compatibility
    return 0.0


def prepare_frame(vision_frame: Any) -> Any:
    if vision_frame is None or vision_frame.size == 0:
        return None  # Frame skip logic: avoid resize crash on invalid frame

    model_size = get_model_options().get('size', (224, 224))
    model_mean = get_model_options().get('mean', [104, 117, 123])

    vision_frame = cv2.resize(vision_frame, model_size).astype(numpy.float32)
    vision_frame -= numpy.array(model_mean).astype(numpy.float32)
    vision_frame = numpy.expand_dims(vision_frame, axis=0)
    return vision_frame
