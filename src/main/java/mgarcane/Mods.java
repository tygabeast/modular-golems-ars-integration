package mgarcane;

import dev.xkmc.l2core.base.effects.EffectUtil;
import dev.xkmc.l2damagetracker.contents.attack.DamageData;
import dev.xkmc.l2damagetracker.contents.attack.DamageModifier;
import dev.xkmc.modulargolems.content.core.StatFilterType;
import dev.xkmc.modulargolems.content.entity.common.AbstractGolemEntity;
import dev.xkmc.modulargolems.content.modifier.base.GolemModifier;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.EvokerFangs;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** The sixteen abilities. Every hook is server-side only, throttled and allocation-light. */
public final class Mods {

	private Mods() {
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

	private static void eff(LivingEntity t, Holder<MobEffect> e, int dur, int amp, AbstractGolemEntity<?, ?> g) {
		EffectUtil.addEffect(t, new MobEffectInstance(e, dur, amp), g);
	}

	private static boolean client(AbstractGolemEntity<?, ?> g) {
		return g.level().isClientSide();
	}

	private static boolean isMagic(net.minecraft.world.damagesource.DamageSource s) {
		if (s.is(DamageTypeTags.WITCH_RESISTANT_TO)) return true;
		var key = s.typeHolder().unwrapKey();
		return key.isPresent() && key.get().location().getNamespace().startsWith("ars_");
	}

	/** Source Gem: heals the golem for a share of the damage it deals. */
	public static class SourceLeech extends GolemModifier {
		public SourceLeech() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void postHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.DefenceMax d, int lv) {
			if (client(g)) return;
			float h = d.getDamageFinal() * 0.1f * lv;
			if (h > 0.01f) g.heal(h);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(0.1 * lv));
		}
	}

	/** Fire essence: sets targets on fire. */
	public static class EmberTouch extends GolemModifier {
		public EmberTouch() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (!client(g)) d.getTarget().igniteForSeconds(2 + lv);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, 2 + lv);
		}
	}

	/** Water essence: chills targets. */
	public static class TidalChill extends GolemModifier {
		public TidalChill() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g)) return;
			var t = d.getTarget();
			eff(t, MobEffects.MOVEMENT_SLOWDOWN, 40 + 20 * lv, lv - 1, g);
			if (lv >= 3) eff(t, MobEffects.WEAKNESS, 60, 0, g);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, (40 + 20 * lv) / 20, lv);
		}
	}

	/** Earth essence: each hit sends a shockwave that splashes and knocks back nearby enemies. */
	public static class Tremor extends GolemModifier {
		public Tremor() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void postHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.DefenceMax d, int lv) {
			if (client(g) || Arc.busy) return;
			LivingEntity t = d.getTarget();
			float splash = d.getDamageFinal() * ArcaneConfig.COMMON.splashFraction.get().floatValue() * lv;
			double r = 1.5 + 0.5 * lv;
			Arc.busy = true;
			try {
				Arc.around(g, t, r, e -> {
					double dx = e.getX() - t.getX(), dz = e.getZ() - t.getZ();
					double len = Math.sqrt(dx * dx + dz * dz);
					if (len > 1e-3) e.push(dx / len * 0.4, 0.25, dz / len * 0.4);
					e.hurtMarked = true;
					if (splash > 0.01f) e.hurt(g.damageSources().mobAttack(g), splash);
					eff(e, MobEffects.MOVEMENT_SLOWDOWN, 30, 0, g);
				});
			} finally {
				Arc.busy = false;
			}
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(ArcaneConfig.COMMON.splashFraction.get() * lv), 1.5 + 0.5 * lv);
		}
	}

	/** Air essence: immune to fall damage; hits knock targets upward. */
	public static class GaleStep extends GolemModifier {
		public GaleStep() {
			super(StatFilterType.MOVEMENT, 2);
		}

		@Override
		public boolean onAttacked(AbstractGolemEntity<?, ?> g, DamageData.Attack d, int lv) {
			return lv > 0 && d.getSource().is(DamageTypeTags.IS_FALL);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g)) return;
			var t = d.getTarget();
			t.push(0, 0.15 + 0.1 * lv, 0);
			t.hurtMarked = true;
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this);
		}
	}

	/** Conjuration essence: summons evoker fangs under the target, in a line leading away from the golem. */
	public static class SpectralFangs extends GolemModifier {
		public SpectralFangs() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g)) return;
			if (!Arc.ready(g, "mg_arcane_fang", Math.max(10, ArcaneConfig.COMMON.fangCooldown.get() / lv))) return;
			var t = d.getTarget();
			var level = (ServerLevel) g.level();
			double dx = t.getX() - g.getX(), dz = t.getZ() - g.getZ();
			double len = Math.sqrt(dx * dx + dz * dz);
			if (len < 1e-3) { dx = 1; dz = 0; len = 1; }
			dx /= len; dz /= len;
			float yaw = (float) (Math.atan2(dz, dx) * 180 / Math.PI) - 90f;
			for (int i = 0; i < lv; i++) {
				double dist = i * 1.3;
				level.addFreshEntity(new EvokerFangs(level, t.getX() + dx * dist, t.getY(), t.getZ() + dz * dist, yaw, i * 3, g));
			}
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, lv, Math.max(10, ArcaneConfig.COMMON.fangCooldown.get() / lv) / 20.0);
		}
	}

	/** Abjuration essence: resists magic damage and slowly regrows absorption. */
	public static class ArcaneWard extends GolemModifier {
		private static final ResourceLocation ID = id("ward");

		public ArcaneWard() {
			super(StatFilterType.HEALTH, 3);
		}

		@Override
		public void onDamaged(AbstractGolemEntity<?, ?> g, DamageData.Defence d, int lv) {
			if (isMagic(d.getSource()))
				d.addDealtModifier(DamageModifier.multTotal(1f - 0.2f * lv, ID));
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || !Arc.every(g, 100)) return;
			float cap = 4f * lv, cur = g.getAbsorptionAmount();
			if (cur < cap) g.setAbsorptionAmount(Math.min(cap, cur + 2f));
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(0.2 * lv), 4 * lv);
		}
	}

	/** Arcane armour: each piece worn adds a level. Resists magic damage and slowly mends the golem. */
	public static class SourceMantle extends GolemModifier {
		private static final ResourceLocation ID = id("mantle");

		public SourceMantle() {
			super(StatFilterType.HEALTH, 4);
		}

		@Override
		public void onDamaged(AbstractGolemEntity<?, ?> g, DamageData.Defence d, int lv) {
			if (isMagic(d.getSource()))
				d.addDealtModifier(DamageModifier.multTotal(1f - (float) (ArcaneConfig.COMMON.mantleReduction.get() * lv), ID));
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || !Arc.every(g, ArcaneConfig.COMMON.mantleInterval.get()) || g.getHealth() >= g.getMaxHealth()) return;
			g.heal((float) (ArcaneConfig.COMMON.mantleHeal.get() * lv));
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(ArcaneConfig.COMMON.mantleReduction.get() * lv), ArcaneConfig.COMMON.mantleHeal.get() * lv,
					ArcaneConfig.COMMON.mantleInterval.get() / 20.0);
		}
	}

	/** Aegis armour: each piece worn adds a level. Resists fire, lightning, freezing and explosion damage. */
	public static class ElementalWard extends GolemModifier {
		private static final ResourceLocation ID = id("ward_elemental");

		public ElementalWard() {
			super(StatFilterType.HEALTH, 4);
		}

		@Override
		public void onDamaged(AbstractGolemEntity<?, ?> g, DamageData.Defence d, int lv) {
			var s = d.getSource();
			if (s.is(DamageTypeTags.IS_FIRE) || s.is(DamageTypeTags.IS_LIGHTNING) || s.is(DamageTypeTags.IS_FREEZING) || s.is(DamageTypeTags.IS_EXPLOSION))
				d.addDealtModifier(DamageModifier.multTotal(1f - (float) (ArcaneConfig.COMMON.wardReduction.get() * lv), ID));
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(ArcaneConfig.COMMON.wardReduction.get() * lv));
		}
	}

	/** Manipulation essence: hits drag the target toward the golem. */
	public static class Telekinesis extends GolemModifier {
		public Telekinesis() {
			super(StatFilterType.ATTACK, 2);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g)) return;
			var t = d.getTarget();
			double dx = g.getX() - t.getX(), dz = g.getZ() - t.getZ();
			double len = Math.sqrt(dx * dx + dz * dz);
			if (len < 1.6) return;
			t.push(dx / len * 0.3 * lv, 0.05, dz / len * 0.3 * lv);
			t.hurtMarked = true;
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this);
		}
	}

	/** Anima essence: killing a target restores the golem's health. */
	public static class SoulSiphon extends GolemModifier {
		public SoulSiphon() {
			super(StatFilterType.HEALTH, 3);
		}

		@Override
		public void postHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.DefenceMax d, int lv) {
			if (client(g) || !d.getTarget().isDeadOrDying()) return;
			g.heal(g.getMaxHealth() * 0.08f * lv);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(0.08 * lv));
		}
	}

	/** Silt essence: blinds targets. */
	public static class Sandblast extends GolemModifier {
		public Sandblast() {
			super(StatFilterType.ATTACK, 2);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (!client(g)) eff(d.getTarget(), MobEffects.BLINDNESS, 40 * lv, 0, g);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, 2 * lv);
		}
	}

	/** Mire essence: an aura that bogs down nearby enemies while the golem fights. */
	public static class Quagmire extends GolemModifier {
		public Quagmire() {
			super(StatFilterType.MASS, 3);
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || g.getTarget() == null) return;
			int iv = ArcaneConfig.COMMON.auraInterval.get();
			if (!Arc.every(g, iv)) return;
			Arc.around(g, 3 + lv, e -> eff(e, MobEffects.MOVEMENT_SLOWDOWN, iv + 20, lv - 1, g));
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, 3 + lv, lv);
		}
	}

	/** Lava essence: melee attackers are set on fire. */
	public static class MoltenShell extends GolemModifier {
		public MoltenShell() {
			super(StatFilterType.HEALTH, 3);
		}

		@Override
		public void postDamaged(AbstractGolemEntity<?, ?> g, DamageData.DefenceMax d, int lv) {
			if (client(g)) return;
			LivingEntity a = d.getAttacker();
			if (a != null && a != g && d.getSource().getDirectEntity() == a) a.igniteForSeconds(2 + lv);
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, 2 + lv);
		}
	}

	/** Cinder essence: an aura of ash that weakens (and from level 2 scorches) nearby enemies. */
	public static class AshCloud extends GolemModifier {
		public AshCloud() {
			super(StatFilterType.MASS, 3);
		}

		@Override
		public void onAiStep(AbstractGolemEntity<?, ?> g, int lv) {
			if (client(g) || g.getTarget() == null) return;
			int iv = ArcaneConfig.COMMON.auraInterval.get();
			if (!Arc.every(g, iv)) return;
			Arc.around(g, 3 + lv, e -> {
				eff(e, MobEffects.WEAKNESS, iv + 20, 0, g);
				if (lv >= 2) e.igniteForSeconds(1);
			});
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, 3 + lv);
		}
	}

	/** Vapor essence: scalding hits deal bonus damage. */
	public static class ScaldingSteam extends GolemModifier {
		private static final ResourceLocation ID = id("steam");

		public ScaldingSteam() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			d.addHurtModifier(DamageModifier.multTotal(1f + 0.15f * lv, ID));
			if (g.level() instanceof ServerLevel sl) {
				var t = d.getTarget();
				sl.sendParticles(ParticleTypes.CLOUD, t.getX(), t.getY() + t.getBbHeight() * 0.5, t.getZ(), 3, 0.2, 0.2, 0.2, 0.01);
			}
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(0.15 * lv));
		}
	}

	/** Tempest essence: hits can call down lightning. The bolt is visual only, so it never sets fires or hurts the
	 *  owner, their pets or the golem; the damage goes to the target and nearby valid enemies. */
	public static class Thunderstrike extends GolemModifier {
		public Thunderstrike() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			if (client(g) || g.getRandom().nextFloat() >= ArcaneConfig.COMMON.lightningChance.get() * lv) return;
			if (!Arc.ready(g, "mg_arcane_bolt", ArcaneConfig.COMMON.lightningCooldown.get())) return;
			var t = d.getTarget();
			var bolt = EntityType.LIGHTNING_BOLT.create(g.level());
			if (bolt == null) return;
			bolt.moveTo(Vec3.atBottomCenterOf(t.blockPosition()));
			bolt.setVisualOnly(true);
			g.level().addFreshEntity(bolt);
			float dmg = ArcaneConfig.COMMON.lightningDamage.get().floatValue();
			var src = g.damageSources().lightningBolt();
			t.hurt(src, dmg);
			t.igniteForSeconds(2);
			Arc.around(g, t, 2.5, e -> {
				e.hurt(src, dmg);
				e.igniteForSeconds(2);
			});
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(ArcaneConfig.COMMON.lightningChance.get() * lv), ArcaneConfig.COMMON.lightningDamage.get(), ArcaneConfig.COMMON.lightningCooldown.get() / 20);
		}
	}

	/** Elemancer shard: every hit cycles through fire, water, earth and air effects, plus bonus damage. */
	public static class ElementalSurge extends GolemModifier {
		private static final ResourceLocation ID = id("surge");

		public ElementalSurge() {
			super(StatFilterType.ATTACK, 3);
		}

		@Override
		public void onHurtTarget(AbstractGolemEntity<?, ?> g, DamageData.Offence d, int lv) {
			d.addHurtModifier(DamageModifier.multTotal(1f + 0.05f * lv, ID));
			if (client(g)) return;
			var pd = g.getPersistentData();
			int step = pd.getInt("mg_arcane_surge");
			pd.putInt("mg_arcane_surge", (step + 1) & 3);
			var t = d.getTarget();
			switch (step) {
				case 0 -> t.igniteForSeconds(2 + lv);
				case 1 -> eff(t, MobEffects.MOVEMENT_SLOWDOWN, 40 + 20 * lv, 1, g);
				case 2 -> eff(t, MobEffects.WEAKNESS, 40 + 20 * lv, 0, g);
				default -> {
					t.push(0, 0.3 + 0.05 * lv, 0);
					t.hurtMarked = true;
				}
			}
		}

		@Override
		public List<MutableComponent> getDetail(int lv) {
			return desc(this, Arc.pct(0.05 * lv));
		}
	}

}
