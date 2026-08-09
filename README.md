MTKPower hint parser for pixel-libperfmgr
===========

Usage
----------
```
python3 main.py refs/powerscntbl.xml refs/powerhint.json
```

Reference configurations
------------------------
Those configurations are based uppon MT6886 platform ([Dimensity 7200 Pro / Ultra](https://www.mediatek.com/products/smartphones/mediatek-dimensity-7200) - [Dimensity 7350 Pro](https://www.mediatek.com/products/smartphones/mediatek-dimensity-7350))

[powerscntbl.xml](refs/powerscntbl.xml)

[powerhint.json](refs/powerhint.json)


Example output
--------------
```
[ROUND] [LAUNCH] CPUEfficiencyClusterMinFreq: 3000000 -> 2000000
[ROUND] [LAUNCH] CPUSuperClusterMinFreq: 3000000 -> 2800000
[INDEX] [LAUNCH] MemFreq: Mapped Index 1 to 3200000000
[ROUND] [AUDIO_STREAMING_LOW_LATENCY] CPUEfficiencyClusterMinFreq: 1000000 -> 1050000
[ROUND] [INTERACTION] CPUEfficiencyClusterMinFreq: 1075000 -> 1100000
[ROUND] [INTERACTION] CPUSuperClusterMinFreq: 1162000 -> 1200000
[ROUND] [INTERACTION] CPUEfficiencyClusterMaxFreq: 3000000 -> 2000000
[ROUND] [INTERACTION] CPUSuperClusterMaxFreq: 3000000 -> 2800000
{
  "Actions": [
    {
      "PowerHint": "LAUNCH",
      "Node": "CPUEfficiencyClusterMinFreq",
      "Duration": 30000,
      "Value": "2000000"
    },
    {
      "PowerHint": "LAUNCH",
      "Node": "CPUSuperClusterMinFreq",
      "Duration": 30000,
      "Value": "2800000"
    },
    {
      "PowerHint": "LAUNCH",
      "Node": "MemFreq",
      "Duration": 30000,
      "Value": "3200000000"
    },
    {
      "PowerHint": "LAUNCH",
      "Node": "UclampTAMin",
      "Duration": 30000,
      "Value": "100"
    },
    {
      "PowerHint": "AUDIO_STREAMING_LOW_LATENCY",
      "Node": "CPUEfficiencyClusterMinFreq",
      "Duration": 0,
      "Value": "1050000"
    },
    {
      "PowerHint": "AUDIO_STREAMING_LOW_LATENCY",
      "Node": "CPUSuperClusterMinFreq",
      "Duration": 0,
      "Value": "1000000"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "CPUEfficiencyClusterMinFreq",
      "Duration": 80,
      "Value": "1100000"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "CPUSuperClusterMinFreq",
      "Duration": 80,
      "Value": "1200000"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "CPUEfficiencyClusterMaxFreq",
      "Duration": 80,
      "Value": "2000000"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "CPUSuperClusterMaxFreq",
      "Duration": 80,
      "Value": "2800000"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "UclampTAMin",
      "Duration": 80,
      "Value": "40"
    },
    {
      "PowerHint": "INTERACTION",
      "Node": "UclampTALatency",
      "Duration": 80,
      "Value": "1"
    }
  ]
}
```