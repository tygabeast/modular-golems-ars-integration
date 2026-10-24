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
	public final ModConfigSpec.DoubleValue recallDistance;
	public final ModConfigSpec.IntValue recallCooldown;
	public final ModConfigSpec.DoubleValue spongeHeal;
	public final ModConfigSpec.DoubleValue lightRadius;
	public final ModConfigSpec.IntValue surgeDuration;
	public final ModConfigSpec.IntValue surgeCooldown;
	public final ModConfigSpec.DoubleValue glyphChance;
	public final ModConfigSpec.IntValue weaponCooldown;
	public final ModConfigSpec.IntValue weaponMaxCost;

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
		b.push("upgrades");
		recallDistance = b.comment("Arcane Recall: blocks from the owner before an idle golem teleports back")
				.defineInRange("recallDistance", 32.0, 8, 256);
		recallCooldown = b.comment("Arcane Recall cooldown in ticks")
				.defineInRange("recallCooldown", 600, 40, 24000);
		spongeHeal = b.comment("Spell Sponge: health restored per magic hit (magic damage is also halved)")
				.defineInRange("spongeHeal", 2.0, 0, 100);
		lightRadius = b.comment("Magelight Core: blocks within which the owner gets Night Vision")
				.defineInRange("lightRadius", 16.0, 2, 128);
		surgeDuration = b.comment("Source Surge: duration of the speed and strength boost, in ticks")
				.defineInRange("surgeDuration", 160, 20, 2400);
		surgeCooldown = b.comment("Source Surge cooldown in ticks")
				.defineInRange("surgeCooldown", 400, 20, 24000);
		glyphChance = b.comment("Glyph Strike: chance per hit to apply a glyph effect (also limited to once per second)")
				.defineInRange("glyphChance", 0.2, 0, 1);
		b.pop();
		b.push("weapons");
		weaponCooldown = b.comment("Arcane weapons: ticks between spell casts for one golem (Ars Nouveau does not charge mana to golems, so this is the limit)")
				.defineInRange("weaponCooldown", 40, 1, 24000);
		weaponMaxCost = b.comment("Arcane weapons: refuse to cast spells whose mana cost is above this. 0 = no limit")
				.defineInRange("weaponMaxCost", 0, 0, 100000);
		b.pop();
	}

}
