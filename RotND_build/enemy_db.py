from Global.const_def import *
from object import *

import json


class EnemyDB:
    @classmethod
    def json_to_dict(self, path) -> dict:
        """Construct dictionary as enemy database with given json file"""
        with open(path) as f:
            enemy_defs: list[dict] = json.load(f)["_enemyDefinitions"]

        enemy_db = {}
        for enemy_def in enemy_defs:
            id = enemy_def.pop("_id")

            # keys of enemy_def:
            #   name, health, total_hits, beat_for_move, priority,
            #   properties, shield, enemy_on_death_id
            enemy_def["name"] = enemy_def["_displayName"]
            enemy_def["health"] = enemy_def["_maxHealth"]
            enemy_def["total_hits"] = enemy_def["_totalHitsAddedToStage"]
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
            # TODO
            if name == GREEN_SLIME:
                setattr(GreenSlime, "beat_for_move", enemy_def["beat_for_move"])
                setattr(GreenSlime, "max_health", enemy_def["health"])
                setattr(GreenSlime, "max_shield", enemy_def["shield"])
            elif name == BLUE_SLIME:
                setattr(BlueSlime, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueSlime, "max_health", enemy_def["health"])
                setattr(BlueSlime, "max_shield", enemy_def["shield"])
            elif name == BLUE_BAT:
                setattr(BlueBat, "beat_for_move", enemy_def["beat_for_move"])
                setattr(BlueBat, "max_health", enemy_def["health"])
                setattr(BlueBat, "max_shield", enemy_def["shield"])
            elif name == YELLOW_BAT:
                setattr(YellowBat, "beat_for_move", enemy_def["beat_for_move"])
                setattr(YellowBat, "max_health", enemy_def["health"])
                setattr(YellowBat, "max_shield", enemy_def["shield"])
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
            elif name == APPLE:
                setattr(Apple, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Apple, "max_health", enemy_def["health"])
                setattr(Apple, "max_shield", enemy_def["shield"])
            elif name == CHEESE:
                setattr(Cheese, "beat_for_move", enemy_def["beat_for_move"])
                setattr(Cheese, "max_health", enemy_def["health"])
                setattr(Cheese, "max_shield", enemy_def["shield"])
