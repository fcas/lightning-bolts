import warnings

import pytest
from pytorch_lightning.utilities.warnings import PossibleUserWarning

from pl_bolts.models.detection.yolo.yolo_config import (
    _create_convolutional,
    _create_maxpool,
    _create_shortcut,
    _create_upsample,
)


@pytest.mark.parametrize(
    "config",
    [
        ({"batch_normalize": 1, "filters": 8, "size": 3, "stride": 1, "pad": 1, "activation": "leaky"}),
        ({"batch_normalize": 0, "filters": 2, "size": 1, "stride": 1, "pad": 1, "activation": "mish"}),
        ({"batch_normalize": 1, "filters": 6, "size": 3, "stride": 2, "pad": 1, "activation": "logistic"}),
        ({"batch_normalize": 0, "filters": 4, "size": 3, "stride": 2, "pad": 0, "activation": "linear"}),
    ],
)
def test_create_convolutional(config, catch_warnings):
    warnings.filterwarnings(
        "ignore",
        message=".*does not have many workers which may be a bottleneck.*",
        category=PossibleUserWarning,
    )

    conv, _ = _create_convolutional(config, [3])

    assert conv.conv.out_channels == config["filters"]
    assert conv.conv.kernel_size == (config["size"], config["size"])
    assert conv.conv.stride == (config["stride"], config["stride"])

    activation = config["activation"]
    pad_size = (config["size"] - 1) // 2 if config["pad"] else 0

    if config["pad"]:
        assert conv.conv.padding == (pad_size, pad_size)

    if config["batch_normalize"]:
        assert len(conv) == 3

    if activation != "linear":
        if activation != "logistic":
            assert activation == conv[-1].__class__.__name__.lower()[: len(activation)]
        elif activation == "logistic":
            assert conv[-1].__class__.__name__.lower() == "sigmoid"


@pytest.mark.parametrize(
    "config",
    [
        (
            {
                "size": 2,
                "stride": 2,
            }
        ),
        (
            {
                "size": 6,
                "stride": 3,
            }
        ),
    ],
)
def test_create_maxpool(config, catch_warnings):
    warnings.filterwarnings(
        "ignore",
        message=".*does not have many workers which may be a bottleneck.*",
        category=PossibleUserWarning,
    )

    pad_size = (config["size"] - 1) // 2
    maxpool, _ = _create_maxpool(config, [3])

    assert maxpool.kernel_size == config["size"]
    assert maxpool.stride == config["stride"]
    assert maxpool.padding == pad_size


@pytest.mark.parametrize(
    "config",
    [
        ({"from": 1, "activation": "linear"}),
        ({"from": 3, "activation": "linear"}),
    ],
)
def test_create_shortcut(config, catch_warnings):
    warnings.filterwarnings(
        "ignore",
        message=".*does not have many workers which may be a bottleneck.*",
        category=PossibleUserWarning,
    )

    shortcut, _ = _create_shortcut(config, [3])

    assert shortcut.source_layer == config["from"]


@pytest.mark.parametrize(
    "config",
    [
        ({"stride": 2}),
        ({"stride": 4}),
    ],
)
def test_create_upsample(config, catch_warnings):
    warnings.filterwarnings(
        "ignore",
        message=".*does not have many workers which may be a bottleneck.*",
        category=PossibleUserWarning,
    )

    upsample, _ = _create_upsample(config, [3])

    assert upsample.scale_factor == float(config["stride"])