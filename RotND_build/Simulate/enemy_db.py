from Global.const_def import *

from Simulate.object import *

import json


class EnemyDB:
    @classmethod
    def json_to_dict(cls, path) -> dict:
        """Construct dictionary as enemy database with given json file"""
        with open(path) as f:
            enemy_defs: list[dict] = json.load(f)["_enemyDefinitions"]

        enemy_db = {}
        for enemy_def in enemy_defs:
            id = enemy_def.pop("_id")

            # keys of enemy_def:
            #   name, health, total_enemies, beat_for_move, priority,
            #   properties, shield, enemy_on_death_id
            enemy_def["name"] = enemy_def["_displayName"]
            enemy_def["health"] = enemy_def["_maxHealth"]
            enemy_def["total_enemies"] = enemy_def["_totalEnemiesGenerated"]
            del enemy_def["_totalEnemiesGenerated"]
            del enemy_def["_playerDamage"]
            del enemy_def["_hpAwardedOnDeath"]
            enemy_def["beat_for_move"] = enemy_def["_updateTempoInBeats"]
            enemy_def["priority"] = enemy_def["_collisionPriority"]
            enemy_def["properties"] = enemy_def["_specialProperties"]
            enemy_def["shield"] = enemy_def["_shieldHealth"]
            del enemy_def["_prefabAssetReference"]
            del enemy_def["_heldPrefabAssetReference"]
            del enemy_def["_bodyEnemyId"]
            del enemy_def["_tailEnemyId"]
            enemy_def["enemy_on_death_id"] = enemy_def["_enemySpawnedOnDeathId"]

            enemy_db[id] = enemy_def

        return enemy_db

    @classmethod
    def init_objs(cls, enemy_db: dict):
        for enemy_def in enemy_db.values():
            name = enemy_def["name"]
            if name == GREEN_SLIME:
                setattr(GreenSlime, "beat_for_move", enemy_def["beat_for_move"])
                setattr(GreenSlime, "max_health", enemy_def["health"])
                setattr(GreenSlime, "max_shield", enemy_def["shield"])
            elif name == BLUE_SLIME:
                setattr(BlueSlime, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueSlime, "max_health", enemy_def["health"])
                setattr(BlueSlime, "max_shield", enemy_def["shield"])
            elif name == YELLOW_SLIME:
                setattr(YellowSlime, "beat_for_move", enemy_def["beat_for_move"])
                setattr(YellowSlime, "max_health", enemy_def["health"])
                setattr(YellowSlime, "max_shield", enemy_def["shield"])
            elif name == BLUE_BAT:
                setattr(BlueBat, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueBat, "max_health", enemy_def["health"])
                setattr(BlueBat, "max_shield", enemy_def["shield"])
            elif name == YELLOW_BAT:
                setattr(YellowBat, "beat_for_move", enemy_def["beat_for_move"])
                setattr(YellowBat, "max_health", enemy_def["health"])
                setattr(YellowBat, "max_shield", enemy_def["shield"])
            elif name == RED_BAT:
                setattr(RedBat, "beat_for_move", enemy_def["beat_for_move"])
                setattr(RedBat, "max_health", enemy_def["health"])
                setattr(RedBat, "max_shield", enemy_def["shield"])
            elif name == GREEN_ZOMBIE:
                setattr(GreenZombie, "beat_for_move", enemy_def["beat_for_move"])
                setattr(GreenZombie, "max_health", enemy_def["health"])
                setattr(GreenZombie, "max_shield", enemy_def["shield"])
            elif name == RED_ZOMBIE:
                setattr(RedZombie, "beat_for_move", enemy_def["beat_for_move"])
                setattr(RedZombie, "max_health", enemy_def["health"])
                setattr(RedZombie, "max_shield", enemy_def["shield"])
            elif name == BASE_SKELETON:
                setattr(BaseSkeleton, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BaseSkeleton, "max_health", enemy_def["health"])
                setattr(BaseSkeleton, "max_shield", enemy_def["shield"])
            elif name == SHIELDED_BASE_SKELETON:
                setattr(
                    ShieldedBaseSkeleton, "beat_for_move", enemy_def["beat_for_move"]
                )
                setattr(ShieldedBaseSkeleton, "max_health", enemy_def["health"])
                setattr(ShieldedBaseSkeleton, "max_shield", enemy_def["shield"])
            elif name == TRIPLE_SHIELD_BASE_SKELETON:
                setattr(
                    DoubleShieldedBaseSkeleton,
                    "beat_for_move",
                    enemy_def["beat_for_move"],
                )
                setattr(DoubleShieldedBaseSkeleton, "max_health", enemy_def["health"])
                setattr(DoubleShieldedBaseSkeleton, "max_shield", enemy_def["shield"])
            elif name == BLUE_ARMADILLO:
                setattr(BlueArmadillo, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueArmadillo, "max_health", enemy_def["health"])
                setattr(BlueArmadillo, "max_shield", enemy_def["shield"])
            elif name == RED_ARMADILLO:
                setattr(RedArmadillo, "beat_for_move", enemy_def["beat_for_move"])
                setattr(RedArmadillo, "max_health", enemy_def["health"])
                setattr(RedArmadillo, "max_shield", enemy_def["shield"])
            elif name == YELLOW_ARMADILLO:
                setattr(YellowArmadillo, "beat_for_move", enemy_def["beat_for_move"])
                setattr(YellowArmadillo, "max_health", enemy_def["health"])
                setattr(YellowArmadillo, "max_shield", enemy_def["shield"])
            elif name == YELLOW_SKELETON:
                setattr(YellowSkeleton, "beat_for_move", enemy_def["beat_for_move"])
                setattr(YellowSkeleton, "max_health", enemy_def["health"])
                setattr(YellowSkeleton, "max_shield", enemy_def["shield"])
            elif name == SHIELDED_YELLOW_SKELETON:
                setattr(
                    ShieldedYellowSkeleton, "beat_for_move", enemy_def["beat_for_move"]
                )
                setattr(ShieldedYellowSkeleton, "max_health", enemy_def["health"])
                setattr(ShieldedYellowSkeleton, "max_shield", enemy_def["shield"])
            elif name == BLACK_SKELETON:
                setattr(BlackSkeleton, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlackSkeleton, "max_health", enemy_def["health"])
                setattr(BlackSkeleton, "max_shield", enemy_def["shield"])
            elif name == SHIELDED_BLACK_SKELETON:
                setattr(
                    ShieldedBlackSkeleton, "beat_for_move", enemy_def["beat_for_move"]
                )
                setattr(ShieldedBlackSkeleton, "max_health", enemy_def["health"])
                setattr(ShieldedBlackSkeleton, "max_shield", enemy_def["shield"])
            elif name == BASE_WYRM:
                setattr(WyrmHead, "beat_for_move", enemy_def["beat_for_move"])
                setattr(WyrmHead, "max_health", enemy_def["health"])
                setattr(WyrmHead, "max_shield", enemy_def["shield"])
            elif name == BASE_HARPY:
                setattr(BaseHarpy, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BaseHarpy, "max_health", enemy_def["health"])
                setattr(BaseHarpy, "max_shield", enemy_def["shield"])
            elif name == BLUE_HARPY:
                setattr(BlueHarpy, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueHarpy, "max_health", enemy_def["health"])
                setattr(BlueHarpy, "max_shield", enemy_def["shield"])
            elif name == RED_HARPY:
                setattr(RedHarpy, "beat_for_move", enemy_def["beat_for_move"])
                setattr(RedHarpy, "max_health", enemy_def["health"])
                setattr(RedHarpy, "max_shield", enemy_def["shield"])
            elif name == APPLE:
                setattr(Apple, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Apple, "max_health", enemy_def["health"])
                setattr(Apple, "max_shield", enemy_def["shield"])
            elif name == CHEESE:
                setattr(Cheese, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Cheese, "max_health", enemy_def["health"])
                setattr(Cheese, "max_shield", enemy_def["shield"])
            elif name == DRUMSTICK:
                setattr(Drumstick, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Drumstick, "max_health", enemy_def["health"])
                setattr(Drumstick, "max_shield", enemy_def["shield"])
            elif name == HAM:
                setattr(Ham, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Ham, "max_health", enemy_def["health"])
                setattr(Ham, "max_shield", enemy_def["shield"])
            elif name == BASE_BLADEMASTER:
                setattr(BaseBlademaster, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BaseBlademaster, "max_health", enemy_def["health"])
                setattr(BaseBlademaster, "max_shield", enemy_def["shield"])
            elif name == STRONG_BLADEMASTER:
                setattr(StrongBlademaster, "beat_for_move", enemy_def["beat_for_move"])
                setattr(StrongBlademaster, "max_health", enemy_def["health"])
                setattr(StrongBlademaster, "max_shield", enemy_def["shield"])
            elif name == BASE_SKULL:
                setattr(BaseSkull, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BaseSkull, "max_health", enemy_def["health"])
                setattr(BaseSkull, "max_shield", enemy_def["shield"])
            elif name == BLUE_SKULL:
                setattr(BlueSkull, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueSkull, "max_health", enemy_def["health"])
                setattr(BlueSkull, "max_shield", enemy_def["shield"])
            elif name == RED_SKULL:
                setattr(RedSkull, "beat_for_move", enemy_def["beat_for_move"])
                setattr(RedSkull, "max_health", enemy_def["health"])
                setattr(RedSkull, "max_shield", enemy_def["shield"])
