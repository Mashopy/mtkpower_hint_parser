import xml.etree.ElementTree as ET
import json
import argparse
from pathlib import Path

def find_closest_value(target_val, available_values, node_name, hint_name):
    try:
        numeric_avail = sorted([int(v) for v in available_values if str(v).isdigit() and int(v) > 0])
        target = int(target_val)
        if str(target_val) in [str(v) for v in available_values]: return str(target_val)
        upscale_options = [v for v in numeric_avail if v >= target]
        result = min(upscale_options) if upscale_options else max(numeric_avail)
        print(f"[ROUND] [{hint_name}] {node_name}: {target_val} -> {result}")
        return str(result)
    except:
        return str(target_val)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file")
    parser.add_argument("json_file")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    # Define standard Primary hints in case they appear in the XML
    PRIMARY_HINTS = ["INTERACTION", "LAUNCH", "AUDIO_STREAMING_LOW_LATENCY", "GAME_LOADING", "GAME", "EXPENSIVE_RENDERING"]

    # Mapping MTK variants to their standard AOSP hints (only if Primary is absent)
    ALIASES = {
        "MTKPOWER_HINT_UX_SCROLLING": "INTERACTION",
        "MTKPOWER_HINT_UX_SCROLLING_COMMON": "INTERACTION",
        "MTKPOWER_HINT_LAUNCH": "LAUNCH",
        "MTKPOWER_HINT_AUDIO_LATENCY_UL": "AUDIO_STREAMING_LOW_LATENCY",
        "MTKPOWER_HINT_EXT_LAUNCH_FOR_GAME": "GAME_LOADING",
        "MTKPOWER_HINT_GAME_MODE": "GAME"
    }

    MTK_MAP = {
        "PERF_RES_CPUFREQ_MIN_CLUSTER_0": {"node": "CPUEfficiencyClusterMinFreq", "type": "value"},
        "PERF_RES_CPUFREQ_MIN_CLUSTER_1": {"node": "CPUSuperClusterMinFreq", "type": "value"},
        "PERF_RES_CPUFREQ_MIN_CLUSTER_2": {"node": "CPUUltraClusterMinFreq", "type": "value"},
        "PERF_RES_CPUFREQ_MAX_CLUSTER_0": {"node": "CPUEfficiencyClusterMaxFreq", "type": "value"},
        "PERF_RES_CPUFREQ_MAX_CLUSTER_1": {"node": "CPUSuperClusterMaxFreq", "type": "value"},
        "PERF_RES_CPUFREQ_MAX_CLUSTER_2": {"node": "CPUUltraClusterMaxFreq", "type": "value"},
        "PERF_RES_CPUFREQ_CCI_FREQ":      {"node": "CciFreq", "type": "value"},
        "PERF_RES_DRAM_OPP_MIN":          {"node": "MemFreq", "type": "index"},
        "PERF_RES_GPU_FREQ_MIN":          {"node": "GpuPwrLevel", "type": "index"},
        "PERF_RES_GPU_GED_TIMER_BASE_DVFS_MARGIN": {"node": "GpuBaseDvfsMargin", "type": "value"},
        "PERF_RES_GPU_GED_LOADING_BASE_DVFS_STEP": {"node": "GpuBaseDvfsStep", "type": "value"},
        "PERF_RES_SCHED_UCLAMP_MIN_TA":   {"node": "UclampTAMin", "type": "value"},
        "PERF_RES_SCHED_PREFER_IDLE_TA":  {"node": "UclampTALatency", "type": "value"}
    }

    try:
        config = json.loads(Path(args.json_file).read_text())
        node_map = {n["Name"]: n["Values"] for n in config.get("Nodes", [])}
        root = ET.parse(args.xml_file).getroot()
    except Exception as e:
        print(f"Error: {e}")
        return

    # Identify which Primary hints are present in the XML
    xml_scenarios = [s.get('powerhint') for s in root.findall('scenario')]
    primaries_found = [h for h in PRIMARY_HINTS if h in xml_scenarios]

    hint_registry = {}

    for scenario in root.findall('scenario'):
        mtk_raw = scenario.get('powerhint')
        
        target_hint = None

        if mtk_raw in PRIMARY_HINTS:
            target_hint = mtk_raw
        elif mtk_raw in ALIASES:
            target_hint = ALIASES[mtk_raw]
            # SKIP VARIANT if the Primary exists in the XML
            if target_hint in primaries_found:
                continue
        
        if not target_hint:
            continue

        if target_hint not in hint_registry:
            hint_registry[target_hint] = {}

        # Use hold time as duration if specified, otherwise default to 0 (instant)
        hold_time = scenario.find("./data[@cmd='PERF_RES_POWER_HINT_HOLD_TIME']")
        duration = int(hold_time.get('param1')) if hold_time is not None else 0

        for data in scenario.findall('data'):
            cmd = data.get('cmd')
            param = data.get('param1')

            if cmd in MTK_MAP:
                mapping = MTK_MAP[cmd]
                node_name = mapping["node"]
                if node_name not in node_map: continue

                avail = node_map[node_name]
                if mapping["type"] == "index":
                    try:
                        idx = int(param)
                        if node_name == "GpuPwrLevel":
                            # GpuPwrLevel uses a reversed index mapping
                            # 0 is a special case that maps to the highest performance level on MTKPower hint values
                            final_val = avail[0] if idx == 0 else avail[len(avail) - 1 - idx]
                            if idx != 0:
                                print(f"[INDEX] [{target_hint}] GpuPwrLevel: Transposed Index {param} to Value {final_val}")
                        else:
                            # Standard index for MemFreq (Direct mapping)
                            idx_clamped = min(max(0, idx), len(avail) - 1)
                            final_val = avail[idx_clamped]
                            print(f"[INDEX] [{target_hint}] {node_name}: Mapped Index {param} to {final_val}")
                    except:
                        final_val = avail[0]
                else:
                    final_val = avail[0] if param == "0" else find_closest_value(param, avail, node_name, target_hint)

                # Merge logic (only for variants when Primary is absent)
                if node_name in hint_registry[target_hint]:
                    try:
                        # Keep highest value for performance stability
                        if int(final_val) > int(hint_registry[target_hint][node_name]['val']):
                            hint_registry[target_hint][node_name] = {'val': final_val, 'dur': duration}
                    except: pass
                else:
                    hint_registry[target_hint][node_name] = {'val': final_val, 'dur': duration}

    final_actions = []
    for hint_name, nodes in hint_registry.items():
        for node_name, data in nodes.items():
            final_actions.append({
                "PowerHint": hint_name,
                "Node": node_name,
                "Duration": data['dur'],
                "Value": data['val']
            })

    # Output wrapped in "Actions": []
    output_obj = {"Actions": final_actions}
    final_json = json.dumps(output_obj, indent=2)
    
    if args.output:
        Path(args.output).write_text(final_json)
    else:
        print(final_json)

if __name__ == "__main__":
    main()
