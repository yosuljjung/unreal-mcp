import unreal

LEVEL = "/Game/Map/mcp_test"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

les.load_level(LEVEL)


def spawn(cls, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), label=None):
    # rot = (pitch, yaw, roll)
    actor = eas.spawn_actor_from_class(
        cls,
        unreal.Vector(loc[0], loc[1], loc[2]),
        unreal.Rotator(roll=rot[2], pitch=rot[0], yaw=rot[1]),
    )
    if label:
        actor.set_actor_label(label)
    return actor


# --- Directional Light (sun) ---
sun = spawn(unreal.DirectionalLight, (0.0, 0.0, 1000.0), (-45.0, -30.0, 0.0), "Sun_DirectionalLight")
sun_comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
sun_comp.set_editor_property("intensity", 6.0)
sun_comp.set_editor_property("atmosphere_sun_light", True)

# --- Sky Atmosphere (sky color / horizon) ---
spawn(unreal.SkyAtmosphere, label="SkyAtmosphere")

# --- Sky Light (ambient, real-time capture from the atmosphere) ---
sky = spawn(unreal.SkyLight, (0.0, 0.0, 1000.0), label="SkyLight")
sky_comp = sky.get_component_by_class(unreal.SkyLightComponent)
sky_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_comp.set_editor_property("real_time_capture", True)

# --- Exponential Height Fog (atmospheric depth) ---
spawn(unreal.ExponentialHeightFog, label="HeightFog")

# --- Volumetric Clouds ---
spawn(unreal.VolumetricCloud, label="VolumetricClouds")

les.save_current_level()
unreal.log("=== [MCP] Lighting/environment set added to /Game/Map/mcp_test ===")
