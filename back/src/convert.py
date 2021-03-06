from config import tempDir
from colorsys import hls_to_rgb
from colorsys import rgb_to_hls
from math import log10
import numpy as np
from operator import itemgetter
from typing import Dict, List, Tuple, Union

def dBFStoGainAmps(dBs: np.ndarray) -> np.ndarray:
  return np.round(10 ** (dBs / 20), 2)

def gainAmpTodBFS(amps: np.ndarray) -> np.ndarray:
  return 20 * np.log10(amps)
  
def normalizeOne(n: Union[int, float], minBound: Union[int, float], maxBound: Union[int, float], newMin: Union[int, float], newMax: Union[int, float], clamped: bool = True) -> Union[int, float]:
  if clamped:
    n = clampOne(n, minBound, maxBound)

  return ((n - minBound) / (maxBound - minBound)) * (newMax - newMin) + newMin

def normalizeAll(arr: np.ndarray, minBound: Union[int, float], maxBound: Union[int, float], newMin: Union[int, float], newMax: Union[int, float], clamped: bool = True) -> np.ndarray:
  if clamped:
    arr = clampAll(arr, minBound, maxBound)

  return ((arr - minBound) / (maxBound - minBound)) * (newMax - newMin) + newMin

def clampOne(n: Union[int, float], minBound: Union[int, float], maxBound: Union[int, float]) -> Union[int, float]:
  return max(minBound, min(maxBound, n))

def clampAll(arr: np.ndarray, minBound: Union[int, float], maxBound: Union[int, float]) -> np.ndarray:
  return np.clip(arr, minBound, maxBound)
 
def quantizeRgb(rgb: Tuple[float]) -> Tuple[int]:
  intRgb = []
  for n in rgb:
    assert 0 <= n <= 1.0
    n = int(clampOne(n, minBound=0, maxBound=1.0) * 256.0)
    if n == 256:
      n = 255

    intRgb.append(n)

  return tuple(intRgb)

def melodyPartsToHexColor(melodyParts: Dict) -> Dict[int, str]:
  melody, volumeChanges, timbreTexture = itemgetter('melody', 'volumeChanges', 'timbreTexture')(melodyParts)
  h = 0.0
  l = volumeChanges[sorted(volumeChanges.keys())[0]]
  s = timbreTexture
  colorTimeMap = dict()
  for t, freq in melody:
    h = freq
    if t in volumeChanges:
      l = volumeChanges[t]

    colorTimeMap[t] = rgbToHex(hls_to_rgb(h, l, s))
  
  return colorTimeMap

def hexColorToMelodyParts(colorTimeMap: Dict[int, str]) -> Dict:
  melody = []
  volumeChanges = {}
  timbreTexture = 0.0
  lastLightness = 0.0
  for i,(t, hexColor) in enumerate(colorTimeMap.items()):
    h, l, s = rgb_to_hls(*hexToRgb(hexColor))
    if i == 0:
      timbreTexture = s

    melody.append((t, h))
    if l != lastLightness:
      volumeChanges[t] = lastLightness = l

  return {
    'melody': melody,
    'volumeChanges': volumeChanges,
    'timbreTexture': timbreTexture
  }
    
def rgbToHex(rgb: Tuple[float]) -> str:
  r, g, b = quantizeRgb(rgb)
  return '#{:02x}{:02x}{:02x}'.format(r, g, b)

# Based off of terrygarcia's stackexchange answer:
# https://stackoverflow.com/a/57777266
def hexToRgb(hexString: str) -> Tuple[int]:
  n = int(hexString[1:], 16)
  b = n % 256.0
  g = (n - b) / 256.0 % 256.0
  r = (n - b) / 256.0 ** 2 - (g / 256.0)
  rgb = normalizeAll([int(r), int(g), int(b)], minBound=0, maxBound=255, newMin=0, newMax=1.0)
  return tuple(rgb)
