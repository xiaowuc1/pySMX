from time import sleep

from loguru import logger

from pysmx.sdk.api import SMXAPI
from pysmx.sdk.config import PackedSensorSettings, SMXStageConfig


def read_integer(prompt, lhs, rhs):
    while True:
        try:
            ret = int(input(prompt).strip())
            if lhs <= ret <= rhs: return ret
        except Exception as e:
            pass
        print("Invalid value returned, needs to be in range {} to {}".format(lhs, rhs))

def main():
    # Create an instance of the API
    smxapi = SMXAPI()

    # Forcefully find stages
    smxapi._find_stages()

    stage_players = smxapi.stages.keys()

    player = read_integer("Which stage are you adjusting sensitivities for? ", 1, 2)

    assert player in [1, 2], "got player value {}".format(player)
    # Grab the old config
    logger.info(f"Grabbing config for p{player}")
    config = smxapi.get_stage_config(player)
    logger.debug(f"Current Config for p{player}:\n{config}")

    update_mapping = [
        ("up", 1),
        ("left", 3),
        ("center", 4),
        ("right", 5),
        ("down", 7),
    ]
    for panel, idx in update_mapping:
        # TODO: support per-FSR thresholds, assume monotone
        fsr_low_threshold = config.panel_settings[idx].fsr_low_threshold
        fsr_high_threshold = config.panel_settings[idx].fsr_high_threshold
        print(idx, fsr_low_threshold, fsr_high_threshold)
        assert len(set(fsr_low_threshold)) == 1, "no support for per-FSR thresholds"
        assert len(set(fsr_high_threshold)) == 1, "no support for per-FSR thresholds"
        lhs = fsr_low_threshold[0]
        rhs = fsr_high_threshold[0]
        c = input("Current thresholds for {} panel are {} and {}, do you want to change them? (Y/N) ".format(panel, lhs, rhs)).upper()
        while c not in ['N', 'Y']: c = input("current thresholds are {} and {}, do you want to change them? (Y/N) ").upper()
        if c == 'N': continue
        nlhs = read_integer("Enter lower threshold for {} panel: [5, 249] ".format(panel), 5, 249)
        nrhs = read_integer("Enter upper threshold for {} panel: [{}, 250] ".format(panel, nlhs+1), nlhs+1, 250)
        config.panel_settings[idx].fsr_low_threshold = [nlhs] * 4
        config.panel_settings[idx].fsr_high_threshold = [nrhs] * 4

    logger.debug("Waiting for config write to be enabled...")
    sleep(1.2)

    logger.debug(f"New Config for p{player}:\n{config}")

    logger.info(f"Updating p{player}")
    smxapi.write_stage_config(player, config)
    logger.debug(f"New Config for p{player}:\n{smxapi.stages[player].config}")

    logger.info("Finished")


if __name__ == "__main__":
    main()
