# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This software may be used and distributed in accordance with
# the terms of the DINOv3 License Agreement.

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Callable, Optional, Union
import numpy as np

from .decoders import ImageDataDecoder, TargetDecoder
from .extended import ExtendedVisionDataset

logger = logging.getLogger("dinov3")
_Target = int


class _Split(Enum):
    TRAIN = "train"
    VAL = "val"
    TEST = "test"

    @property
    def length(self) -> int:
        # Para o dataset de soja, o tamanho será calculado dinamicamente
        # baseado no número real de patches encontrados
        return -1  # Indica que deve ser calculado dinamicamente

    def get_dirname(self, class_id: Optional[str] = None) -> str:
        # Para soja: train/soja ou val/soja
        return self.value if class_id is None else os.path.join(self.value, class_id)


class Soja(ExtendedVisionDataset):
    """
    Dataset customizado para patches de soja.
    
    Estrutura esperada:
    root/
    ├── train/
    │   └── soja/
    │       ├── img_0001.jpg
    │       ├── img_0002.jpg
    │       └── ...
    ├── val/
    │   └── soja/
    │       ├── img_0001.jpg
    │       └── ...
    └── extra/
        ├── entries-TRAIN.npy
        └── entries-VAL.npy
    """
    
    Target = Union[_Target]
    Split = Union[_Split]

    def __init__(
        self,
        *,
        split: "Soja.Split",
        root: str,
        extra: str,
        transforms: Optional[Callable] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            root=root,
            transforms=transforms,
            transform=transform,
            target_transform=target_transform,
            image_decoder=ImageDataDecoder,
            target_decoder=TargetDecoder,
        )
        self._extra_root = extra
        self._split = split
        self._entries = None
        
        # Inicializar automaticamente
        self._initialize_dataset()

    @property
    def split(self) -> "Soja.Split":
        return self._split

    def _get_extra_full_path(self, extra_path: str) -> str:
        return os.path.join(self._extra_root, extra_path)

    def _entries_exist(self) -> bool:
        """Verifica se o arquivo entries existe"""
        entries_path = self._get_extra_full_path(self._entries_path)
        return os.path.exists(entries_path)

    def _load_extra(self, extra_path: str) -> np.ndarray:
        extra_full_path = self._get_extra_full_path(extra_path)
        return np.load(extra_full_path, mmap_mode="r")

    def _save_extra(self, extra_array: np.ndarray, extra_path: str) -> None:
        extra_full_path = self._get_extra_full_path(extra_path)
        os.makedirs(self._extra_root, exist_ok=True)
        np.save(extra_full_path, extra_array)

    @property
    def _entries_path(self) -> str:
        return f"entries-{self._split.value.upper()}.npy"

    def _get_entries(self) -> np.ndarray:
        if self._entries is None:
            self._entries = self._load_extra(self._entries_path)
        assert self._entries is not None
        return self._entries

    def _find_images(self) -> list:
        """Encontra todas as imagens no diretório do split"""
        split_dir = Path(self.root) / self._split.value / "soja"
        
        if not split_dir.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {split_dir}")
        
        # Extensões suportadas
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.JPG', '*.JPEG', '*.PNG']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(list(split_dir.glob(ext)))
        
        # Ordenar para consistência
        image_files.sort()
        
        logger.info(f"Encontradas {len(image_files)} imagens em {split_dir}")
        return image_files

    def _create_entries(self) -> None:
        """Cria o arquivo de entries"""
        image_files = self._find_images()
        
        if not image_files:
            raise RuntimeError(f"Nenhuma imagem encontrada para split {self._split.value}")
        
        # Determinar tamanho máximo do path
        max_path_len = max(len(f"{self._split.value}/soja/{img.name}") for img in image_files) + 20
        
        # Criar dtype estruturado compatível com memory mapping
        entries_dtype = np.dtype([
            ('path', f'U{max_path_len}'),
            ('class_id', np.int32)
        ])
        
        # Criar array de entries
        entries_array = np.empty(len(image_files), dtype=entries_dtype)
        
        for i, img_file in enumerate(image_files):
            rel_path = f"{self._split.value}/soja/{img_file.name}"
            entries_array[i] = (rel_path, 0)  # classe 0 para todos
        
        # Salvar
        logger.info(f'Salvando {len(entries_array)} entries em "{self._entries_path}"')
        self._save_extra(entries_array, self._entries_path)

    def _initialize_dataset(self) -> None:
        """Inicializa o dataset criando arquivos necessários se não existirem"""
        entries_full_path = self._get_extra_full_path(self._entries_path)
        
        if not os.path.exists(entries_full_path):
            logger.info(f"Inicializando dataset de patches de soja em {self.root}")
            self._create_entries()

    def get_image_data(self, index: int) -> bytes:
        """Carrega os dados da imagem"""
        entries = self._get_entries()
        rel_path = entries[index]['path']
        
        image_full_path = os.path.join(self.root, rel_path)
        
        if not os.path.exists(image_full_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_full_path}")
        
        with open(image_full_path, mode="rb") as f:
            image_data = f.read()
        return image_data

    def get_target(self, index: int) -> Optional[_Target]:
        """Retorna o target (sempre 0 para soja)"""
        entries = self._get_entries()
        return int(entries[index]['class_id'])

    def get_targets(self) -> Optional[np.ndarray]:
        """Retorna todos os targets"""
        entries = self._get_entries()
        return entries['class_id']

    def __len__(self) -> int:
        """Retorna o número de amostras"""
        entries = self._get_entries()
        return len(entries)

    def dump_extra(self) -> None:
        """Cria todos os arquivos extras necessários"""
        self._create_entries()
        logger.info(f"Dataset de soja inicializado com sucesso para split {self._split.value}!")