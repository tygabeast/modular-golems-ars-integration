package mgarcane;

import dev.xkmc.l2damagetracker.contents.attack.DamageData;
import dev.xkmc.l2damagetracker.contents.attack.DamageModifier;
import dev.xkmc.modulargolems.content.core.StatFilterType;
import dev.xkmc.modulargolems.content.entity.common.AbstractGolemEntity;
import dev.xkmc.modulargolems.content.modifier.base.GolemModifier;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

import java.util.List;

/**
 * The five Ars upgrades. Each is a normal Modular Golems upgrade item (see ArcaneReg) that gives the golem one of these
 * modifiers. Like the material abilities, every hook is server-side only, throttled and allocation-light, and none of
 * them references Ars classes (Ars effects are looked up by id and skipped when absent).
 */
public final class Upgrades {

	private Upgrades() {
	}

	private static ResourceLocation id(String s) {
		return ResourceLocation.fromNamespaceAndPath(MGArcane.MODID, s);
	}

	private static MutableComponent n(Object s) {
		return Component.literal(String.valueOf(s)).withStyle(ChatFormatting.AQUA);
	}

	private static List<MutableComponent> desc(GolemModifier m, Object... args) {
		MutableComponent[] a = new MutableComponent[args.length];
		for (int i = 0; i < a.length; i++) a[i] = n(args[i]);
		return List.of(Component.translatable(m.getDescriptionId() + ".desc", (Object[]) a).withStyle(ChatFormatting.GREEN));
	}

	private static boolean client(AbstractGolemEntity<?, ?> g) {
		return g.level().isClientSide();
	}

	private static boolean isMagic(net.minecraft.world.damagesource.DamageSource s) {
		if (s.is(DamageTypeTags.WITCH_RESISTANT_TO)) return true;
		var key = s.typeHolder().unwrapKey();
		return key.isPresent() && key.get().location().getNamespace().startsWith("ars_");
	}

	/** Looks up an effect by id (Ars effects are optional at runtime); null when it does not exist. */
	private static Holder<MobEffect> effect(String ns, String path) {
		return BuiltInRegistries.MOB_EFFECT.getHolder(ResourceLocation.fromNamespaceAndPath(ns, path)).map(h -> (Holder<MobEffect>) h).orElse(null);
	}

	/** Arcane Recall: a golem that strays too far from its owner while idle blinks back to them. */
	public static class ArcaneRecall extends GolemModifier {
		public ArcaneRecall() {
			super(StatFilterType.MOVEMENT, 1);
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || !Arc.every(g, 40)) return;
			LivingEntity owner = g.getOwner();
			if (owner == null || owner.level() != g.level() || g.isInSittingPose() || g.isPassenger() || g.getTarget() != null) return;
			double far = ArcaneConfig.COMMON.recallDistance.get();
			if (g.distanceToSqr(owner) < far * far) return;
			if (!Arc.ready(g, "mg_arcane_recall", ArcaneConfig.COMMON.recallCooldown.get())) return;
			var rnd = g.getRandom();
			for (int i = 0; i < 4; i++) {
				double a = rnd.nextDouble() * Math.PI * 2, r = 1.5 + rnd.nextDouble() * 1.5;
				double x = owner.getX() + Math.cos(a) * r, z = owner.getZ() + Math.sin(a) * r;
				if (g.randomTeleport(x, owner.getY(), z, true)) {
					if (g.level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.PORTAL, g.getX(), g.getY() + 1, g.getZ(), 20, 0.4, 0.8, 0.4, 0.1);
					g.level().playSound(null, g.blockPosition(), net.minecraft.sounds.SoundEvents.ENDERMAN_TELEPORT, net.minecraft.sounds.SoundSource.NEUTRAL, 0.6f, 1.2f);
					return;
				}
			}
			g.getPersistentData().putLong("mg_arcane_recall", 0L); // nowhere to land: try again soon
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, ArcaneConfig.COMMON.recallDistance.get().intValue(), ArcaneConfig.COMMON.recallCooldown.get() / 20);
		}
	}

	/** Spell Sponge: magic damage is halved and each magic hit heals the golem a little. */
	public static class SpellSponge extends GolemModifier {
		private static final ResourceLocation ID = id("sponge");

		public SpellSponge() {
			super(StatFilterType.HEALTH, 1);
		}

		@Override
		public void onDamaged(AbstractGolemEntity<?, ?> g, DamageData.Defence d, int lv) {
			if (!isMagic(d.getSource())) return;
			d.addDealtModifier(DamageModifier.multTotal(0.5f, ID));
			if (!client(g)) g.heal(ArcaneConfig.COMMON.spongeHeal.get().floatValue());
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, ArcaneConfig.COMMON.spongeHeal.get());
		}
	}

	/** Magelight Core: the golem's glow lets its owner see in the dark while close by. */
	public static class MagelightCore extends GolemModifier {
		public MagelightCore() {
			super(StatFilterType.HEAD, 1);
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || !Arc.every(g, 100)) return;
			LivingEntity owner = g.getOwner();
			double r = ArcaneConfig.COMMON.lightRadius.get();
			if (owner == null || owner.level() != g.level() || g.distanceToSqr(owner) > r * r) return;
			var cur = owner.getEffect(MobEffects.NIGHT_VISION);
			if (cur != null && cur.getDuration() > 300) return;
			owner.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false, true));
			if (g.level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.END_ROD, g.getX(), g.getY() + g.getBbHeight() + 0.2, g.getZ(), 2, 0.2, 0.1, 0.2, 0.01);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, ArcaneConfig.COMMON.lightRadius.get().intValue());
		}
	}

	/** Source Surge: when a mob hits the owner, the golem surges with speed and strength for a few seconds. */
	public static class SourceSurge extends GolemModifier {
		public SourceSurge() {
			super(StatFilterType.ATTACK, 1);
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || !Arc.every(g, 5)) return;
			LivingEntity owner = g.getOwner();
			if (owner == null || owner.level() != g.level() || g.distanceToSqr(owner) > 1024) return;
			if (owner.tickCount - owner.getLastHurtByMobTimestamp() > 10) return;
			if (!Arc.ready(g, "mg_arcane_sourcesurge", ArcaneConfig.COMMON.surgeCooldown.get())) return;
			int dur = ArcaneConfig.COMMON.surgeDuration.get();
			g.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, dur, 1));
			g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, dur, 0));
			if (g.level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.ENCHANT, g.getX(), g.getY() + 1, g.getZ(), 16, 0.4, 0.8, 0.4, 0.2);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, ArcaneConfig.COMMON.surgeDuration.get() / 20, ArcaneConfig.COMMON.surgeCooldown.get() / 20);
		}
	}

	/** Glyph Strike: hits sometimes lay a glyph effect on the target (Hex, Shocked or Snared when Ars provides them). */
	public static class GlyphStrike extends GolemModifier {
		private static final String[] GLYPHS = {"hex", "shocked", "snared"};

		public GlyphStrike() {
			super(StatFilterType.ATTACK, 1);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g) || g.getRandom().nextFloat() >= ArcaneConfig.COMMON.glyphChance.get()) return;
			if (!Arc.ready(g, "mg_arcane_glyph", 20)) return;
			Holder<MobEffect> e = effect("ars_nouveau", GLYPHS[g.getRandom().nextInt(GLYPHS.length)]);
			if (e == null) e = MobEffects.MOVEMENT_SLOWDOWN;
			d.getTarget().addEffect(new MobEffectInstance(e, 100, 0), g);
			if (g.level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.WITCH, d.getTarget().getX(), d.getTarget().getY() + 1, d.getTarget().getZ(), 10, 0.3, 0.5, 0.3, 0.1);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(ArcaneConfig.COMMON.glyphChance.get()));
		}
	}

}
