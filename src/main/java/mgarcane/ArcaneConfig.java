package mgarcane;

import net.neoforged.neoforge.common.ModConfigSpec;

public class ArcaneConfig {

	/** Who area abilities (auras, shockwaves, chain effects) may affect besides the golem's own attack target. */
	public enum Targets { HOSTILE, ALL_MOBS, ALL_MOBS_AND_PLAYERS }

	public static final ModConfigSpec SPEC;
	public static final ArcaneConfig COMMON;

	static {
		var pair = new ModConfigSpec.Builder().configure(ArcaneConfig::new);
		COMMON = pair.getLeft();
		SPEC = pair.getRight();
	}

	public final ModConfigSpec.EnumValue<Targets> targets;
	public final ModConfigSpec.IntValue auraInterval;
	public final ModConfigSpec.DoubleValue splashFraction;
	public final ModConfigSpec.IntValue fangCooldown;
	public final ModConfigSpec.IntValue lightningCooldown;
	public final ModConfigSpec.DoubleValue lightningChance;
	public final ModConfigSpec.DoubleValue lightningDamage;

	private ArcaneConfig(ModConfigSpec.Builder b) {
		b.push("arcane");
		targets = b.comment("Who area abilities (Tremor, Quagmire, Ash Cloud) may affect besides the golem's own target.",
						"HOSTILE = hostile monsters only (default), ALL_MOBS = every mob that is not owned by the golem's owner,",
						"ALL_MOBS_AND_PLAYERS = also other players (never the owner)")
				.defineEnum("targets", Targets.HOSTILE);
		auraInterval = b.comment("Ticks between aura scans (Quagmire, Ash Cloud). Higher is cheaper. Auras only scan while the golem has a target.")
				.defineInRange("auraInterval", 20, 5, 200);
		splashFraction = b.comment("Tremor splash damage as a fraction of the hit, per level")
				.defineInRange("splashFraction", 0.3, 0, 2);
		fangCooldown = b.comment("Spectral Fangs cooldown in ticks (divided by level)")
				.defineInRange("fangCooldown", 80, 10, 2000);
		lightningCooldown = b.comment("Thunderstrike cooldown in ticks")
				.defineInRange("lightningCooldown", 100, 20, 2000);
		lightningChance = b.comment("Thunderstrike chance per hit, per level")
				.defineInRange("lightningChance", 0.15, 0, 1);
		lightningDamage = b.comment("Thunderstrike damage to the target and enemies within 2.5 blocks of it")
				.defineInRange("lightningDamage", 8.0, 0, 200);
		b.pop();
	}

}
