package mgarcane;

import com.tterrag.registrate.util.nullness.NonNullSupplier;
import dev.xkmc.modulargolems.content.item.upgrade.CraftMaterialItem;
import dev.xkmc.modulargolems.content.modifier.base.GolemModifier;
import dev.xkmc.modulargolems.init.ModularGolems;
import dev.xkmc.modulargolems.init.registrate.GolemModifiers;
import net.neoforged.fml.ModList;


/**
 * Registered through Modular Golems' own registrate under the "modulargolems" namespace,
 * like the built-in Alex's Caves / Cataclysm integrations (modulargolems:arcane_fire_construct, ...).
 * Ars Elemental / Ars Elemancy are optional: their constructs and abilities only exist when the mod is present.
 */
public class ArcaneReg {

	private static final String NOUVEAU = "ars_nouveau", ELEMENTAL = "ars_elemental", ELEMANCY = "ars_elemancy";

	private static <T extends GolemModifier> void mat(String ns, String key, String id, NonNullSupplier<T> mod, String desc) {
		if (!ModList.get().isLoaded(ns)) return;
		ModularGolems.REGISTRATE.item("arcane_" + key + "_construct", CraftMaterialItem::new).register();
		GolemModifiers.reg(id, mod, desc);
	}

	static {
		mat(NOUVEAU, "source_gem", "source_leech", Mods.SourceLeech::new, "Heal %s of the damage dealt");
		mat(NOUVEAU, "fire", "ember_touch", Mods.EmberTouch::new, "Set attack targets on fire for %s seconds");
		mat(NOUVEAU, "water", "tidal_chill", Mods.TidalChill::new, "Slow attack targets for %s seconds (Slowness %s)");
		mat(NOUVEAU, "earth", "tremor", Mods.Tremor::new, "Hits splash %s of their damage to nearby enemies within %s blocks and knock them back");
		mat(NOUVEAU, "air", "gale_step", Mods.GaleStep::new, "Immune to fall damage. Hits knock targets upward");
		mat(NOUVEAU, "conjuration", "spectral_fangs", Mods.SpectralFangs::new, "Hits summon %s spectral fang(s) under the target, once every %s seconds");
		mat(NOUVEAU, "abjuration", "arcane_ward", Mods.ArcaneWard::new, "Take %s less magic damage and slowly regrow up to %s absorption");
		mat(NOUVEAU, "manipulation", "telekinesis", Mods.Telekinesis::new, "Hits drag the target toward the golem");
		mat(ELEMENTAL, "anima", "soul_siphon", Mods.SoulSiphon::new, "Killing a target heals %s of max health");
		mat(ELEMANCY, "silt", "sandblast", Mods.Sandblast::new, "Blind attack targets for %s seconds");
		mat(ELEMANCY, "lava", "molten_shell", Mods.MoltenShell::new, "Melee attackers are set on fire for %s seconds");
		mat(ELEMANCY, "mire", "quagmire", Mods.Quagmire::new, "Enemies within %s blocks are slowed (Slowness %s) while the golem fights");
		mat(ELEMANCY, "cinder", "ash_cloud", Mods.AshCloud::new, "Enemies within %s blocks are weakened while the golem fights");
		mat(ELEMANCY, "vapor", "scalding_steam", Mods.ScaldingSteam::new, "Hits deal %s extra damage");
		mat(ELEMANCY, "tempest", "thunderstrike", Mods.Thunderstrike::new, "Hits have a %s chance to call lightning for %s damage (cooldown %s seconds)");
		mat(ELEMANCY, "shard", "elemental_surge", Mods.ElementalSurge::new, "Hits deal %s extra damage and cycle burn, chill, weaken and launch");
	}

	public static void register() {
		// class initialisation performs all registration
	}

}
