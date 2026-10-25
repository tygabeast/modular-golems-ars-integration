package mgarcane;

import com.hollingsworth.arsnouveau.api.item.ICasterTool;
import com.hollingsworth.arsnouveau.api.spell.AbstractCastMethod;
import com.hollingsworth.arsnouveau.api.spell.AbstractCaster;
import com.hollingsworth.arsnouveau.api.spell.AbstractSpellPart;
import com.hollingsworth.arsnouveau.api.spell.EntitySpellResolver;
import com.hollingsworth.arsnouveau.api.spell.Spell;
import com.hollingsworth.arsnouveau.api.spell.SpellCaster;
import com.hollingsworth.arsnouveau.api.spell.SpellContext;
import com.hollingsworth.arsnouveau.api.spell.wrapped_caster.LivingCaster;
import com.hollingsworth.arsnouveau.common.entity.EntitySpellArrow;
import com.hollingsworth.arsnouveau.common.spell.augment.AugmentAccelerate;
import com.hollingsworth.arsnouveau.common.spell.method.MethodProjectile;
import com.hollingsworth.arsnouveau.common.spell.method.MethodTouch;
import com.hollingsworth.arsnouveau.common.util.PortUtil;
import com.hollingsworth.arsnouveau.setup.registry.DataComponentRegistry;
import dev.xkmc.l2damagetracker.contents.attack.DamageData;
import dev.xkmc.modulargolems.content.entity.metalgolem.MetalGolemEntity;
import dev.xkmc.modulargolems.content.item.equipments.IAttackListenerWeapon;
import dev.xkmc.modulargolems.content.item.equipments.MetalGolemWeaponItem;
import dev.xkmc.modulargolems.content.item.ranged.CannonPoseUtil;
import dev.xkmc.modulargolems.content.item.ranged.GolemMechaBowBehavior;
import dev.xkmc.modulargolems.content.item.ranged.IShoulderCannonAnimated;
import dev.xkmc.modulargolems.content.item.ranged.ShouldWeaponItem;
import dev.xkmc.modulargolems.content.client.armor.GolemModelPaths;
import dev.xkmc.modulargolems.content.item.ranged.MetalGolemBowItem;
import dev.xkmc.modulargolems.content.item.ranged.MetalGolemMechaBowItem;
import dev.xkmc.modulargolems.init.ModularGolems;
import dev.xkmc.modulargolems.init.material.GolemWeaponType;
import dev.xkmc.modulargolems.init.material.IGolemWeaponFactory;
import dev.xkmc.modulargolems.init.material.IGolemWeaponMaterial;
import dev.xkmc.mob_weapon_api.api.projectile.BowUseContext;
import dev.xkmc.mob_weapon_api.api.projectile.ProjectileWeaponUser;
import dev.xkmc.mob_weapon_api.registry.WeaponRegistry;
import dev.xkmc.mob_weapon_api.registry.WeaponStatus;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.item.Items;
import net.minecraft.sounds.SoundEvents;
import net.neoforged.fml.event.lifecycle.FMLLoadCompleteEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Golem weapons that cast an Ars Nouveau spell on hit, set up on the Scribe's Table exactly like the Enchanter's Sword.
 * Ars never charges a non-player caster, so the limit is a per-golem cooldown (and an optional spell cost cap) in the config.
 * This class is only loaded when Ars Nouveau is present.
 */
public final class CasterWeapons {

	private static final String COOLDOWN_KEY = "mg_arcane_cast";

	private CasterWeapons() {
	}

	// ---- shared casting ---------------------------------------------------------------------------------------------

	/** Casts the spell stored on `stack` at `target` on behalf of the golem. Server side, cooldown and cost cap applied. */
	static void cast(LivingEntity golem, ItemStack stack, ICasterTool tool, Entity target) {
		if (!(golem.level() instanceof ServerLevel sl) || target == null || !target.isAlive()) return;
		AbstractCaster<?> caster = tool.getSpellCaster(stack);
		if (caster == null) return;   // not scribed yet (items made by an older version have no caster data)
		Spell spell = caster.getSpell();
		if (spell.isEmpty()) return;
		int cap = ArcaneConfig.COMMON.weaponMaxCost.get();
		if (cap > 0 && spell.getCost() > cap) return;
		if (!Arc.ready(golem, COOLDOWN_KEY, ArcaneConfig.COMMON.weaponCooldown.get())) return;
		Spell s = caster.modifySpellBeforeCasting(sl, golem, InteractionHand.MAIN_HAND, spell);
		SpellContext ctx = new SpellContext(sl, s, golem, new LivingCaster(golem), stack);
		new EntitySpellResolver(ctx).onCastOnEntity(stack, target, InteractionHand.MAIN_HAND);
	}

	/** Weapons take any spell without a Form glyph (the weapon supplies Touch), like the Enchanter's Sword. */
	static boolean noForm(Spell spell) {
		for (AbstractSpellPart p : spell.unsafeList()) if (p instanceof AbstractCastMethod) return false;
		return true;
	}

	static void touchFirst(Spell.Mutable spell) {
		prepend(spell, MethodTouch.INSTANCE);
	}

	static void prepend(Spell.Mutable spell, AbstractSpellPart first) {
		List<AbstractSpellPart> list = new ArrayList<>();
		list.add(first);
		list.addAll(spell.recipe);
		spell.recipe = list;
	}

	/** Every caster item starts with an empty spell caster component; without it the Scribe's Table cannot scribe it. */
	static Item.Properties withCaster(Item.Properties p) {
		return p.component(DataComponentRegistry.SPELL_CASTER.get(), new SpellCaster());
	}

	// ---- melee ------------------------------------------------------------------------------------------------------

	public static class Weapon extends MetalGolemWeaponItem implements ICasterTool, IAttackListenerWeapon {

		public Weapon(Item.Properties p, int damage, double range, float a, float b) {
			super(p, damage, range, a, b);
		}

		@Override
		public boolean isScribedSpellValid(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell spell) {
			return noForm(spell);
		}

		@Override
		public void sendInvalidMessage(Player player) {
			PortUtil.sendMessageNoSpam(player, Component.translatable("ars_nouveau.sword.invalid"));
		}

		@Override
		public void scribeModifiedSpell(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell.Mutable spell) {
			touchFirst(spell);
		}

		@Override
		public void onAttack(DamageData.Attack data, DamageSource source, MetalGolemEntity golem, ItemStack stack) {
			if (golem.level().isClientSide()) return;
			cast(golem, stack, this, data.getTarget());
		}

		@Override
		public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
			super.appendHoverText(stack, ctx, list, flag);
			Tips.text(this, stack, ctx, list, flag);
		}

		@Override
		public java.util.Optional<net.minecraft.world.inventory.tooltip.TooltipComponent> getTooltipImage(ItemStack stack) {
			return Tips.image(this, stack);
		}
	}

	// ---- ranged -----------------------------------------------------------------------------------------------------

	/**
	 * Works like the Enchanter's Bow: the Scribe's Table puts a Projectile glyph in front of the scribed spell (a spell with its
	 * own Form glyph is refused), and each shot is a spell arrow that resolves the spell where it lands. No arrows are needed.
	 * An un-scribed Arcane Mecha Bow is a normal Mecha Bow and shoots ordinary arrows.
	 */
	public static class Bow extends MetalGolemMechaBowItem implements ICasterTool {

		public Bow(Item.Properties p) {
			super(withCaster(p), 30, 5);
		}

		@Override
		public boolean isScribedSpellValid(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell spell) {
			return noForm(spell);
		}

		@Override
		public void sendInvalidMessage(Player player) {
			PortUtil.sendMessageNoSpam(player, Component.translatable("ars_nouveau.sword.invalid"));
		}

		@Override
		public void scribeModifiedSpell(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell.Mutable spell) {
			prepend(spell, MethodProjectile.INSTANCE);
		}

		@Override
		public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
			super.appendHoverText(stack, ctx, list, flag);
			Tips.text(this, stack, ctx, list, flag);
		}

		@Override
		public java.util.Optional<net.minecraft.world.inventory.tooltip.TooltipComponent> getTooltipImage(ItemStack stack) {
			return Tips.image(this, stack);
		}
	}

	/** The spell a golem may fire from `stack` right now (scribed, within the cost cap), or null. */
	private static Spell armedSpell(ItemStack stack) {
		if (!(stack.getItem() instanceof Bow bow)) return null;
		AbstractCaster<?> caster = bow.getSpellCaster(stack);
		if (caster == null) return null;
		Spell spell = caster.getSpell();
		if (spell.isEmpty()) return null;
		int cap = ArcaneConfig.COMMON.weaponMaxCost.get();
		return cap > 0 && spell.getCost() > cap ? null : spell;
	}

	/** Modular Golems' bow AI, except a scribed Arcane Mecha Bow needs no arrows and fires spell arrows instead. */
	static class BowBehavior extends GolemMechaBowBehavior {

		@Override
		public boolean hasProjectile(ProjectileWeaponUser user, ItemStack stack) {
			if (stack.getItem() instanceof MetalGolemBowItem item && item.isFor(user.user().getType()) && armedSpell(stack) != null)
				return true;
			return super.hasProjectile(user, stack);
		}

		@Override
		public int shootArrow(BowUseContext ctx, float power, ItemStack stack, InteractionHand hand) {
			Spell spell = armedSpell(stack);
			if (spell == null) return super.shootArrow(ctx, power, stack, hand);
			LivingEntity golem = ctx.user();
			if (!(golem.level() instanceof ServerLevel sl) || !(golem instanceof Mob mob) || mob.getTarget() == null) return 20;
			if (!Arc.ready(golem, COOLDOWN_KEY, ArcaneConfig.COMMON.weaponCooldown.get())) return 20;
			Bow bow = (Bow) stack.getItem();
			AbstractCaster<?> caster = bow.getSpellCaster(stack);
			Spell s = caster.modifySpellBeforeCasting(sl, golem, hand, spell);
			SpellContext sc = new SpellContext(sl, s, golem, new LivingCaster(golem), stack);
			EntitySpellArrow arrow = new EntitySpellArrow(sl, golem, new ItemStack(Items.ARROW), stack, new EntitySpellResolver(sc));
			arrow.setBaseDamage(1.0);
			arrow.pickup = AbstractArrow.Pickup.DISALLOWED;
			ctx.aim(arrow.position(), power * ctx.getInitialVelocityFactor(), arrow.isNoGravity() ? 0f : 0.05f, ctx.getInitialInaccuracy()).shoot(arrow, 0f);
			sl.addFreshEntity(arrow);
			golem.playSound(SoundEvents.ARROW_SHOOT, 1f, 1f / (golem.getRandom().nextFloat() * 0.4f + 0.8f));
			return 35;
		}
	}

	/**
	 * Modular Golems registers one bow behaviour for every golem bow. This swaps that entry (same key, same place in the
	 * lookup order) for one that hands Arcane Mecha Bows to {@link BowBehavior} and everything else to the original.
	 */
	static void onLoadComplete(FMLLoadCompleteEvent e) {
		e.enqueueWork(() -> WeaponRegistry.BOW.register(ModularGolems.loc("golem_bow"),
				stack -> WeaponStatus.RANGED.of(stack.getItem() instanceof MetalGolemBowItem),
				(user, stack) -> stack.getItem() instanceof Bow ? new BowBehavior() : new GolemMechaBowBehavior(), 10));
	}


	// ---- shoulder ---------------------------------------------------------------------------------------------------

	/**
	 * Works like the Enchanter's Wand, worn on a Metal Golem's shoulder: the Scribe's Table puts Projectile and Accelerate in
	 * front of the scribed spell (a spell with its own Form glyph is refused) and the golem fires it at its target.
	 * It reuses the Beacon Cannon's shoulder model, pose and swing-up animation, painted as a wand.
	 */
	public static class ShoulderWand extends ShouldWeaponItem implements ICasterTool, IShoulderCannonAnimated {

		public ShoulderWand(Item.Properties p) {
			super(withCaster(p.stacksTo(1)));
		}

		@Override
		public boolean isScribedSpellValid(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell spell) {
			return noForm(spell);
		}

		@Override
		public void sendInvalidMessage(Player player) {
			PortUtil.sendMessageNoSpam(player, Component.translatable("ars_nouveau.wand.invalid"));
		}

		@Override
		public void scribeModifiedSpell(AbstractCaster<?> caster, Player player, InteractionHand hand, ItemStack stack, Spell.Mutable spell) {
			List<AbstractSpellPart> list = new ArrayList<>();
			list.add(MethodProjectile.INSTANCE);
			list.add(AugmentAccelerate.INSTANCE);
			list.addAll(spell.recipe);
			spell.recipe = list;
		}

		@Override
		public ResourceLocation getModelForHand(InteractionHand hand) {
			return hand == InteractionHand.MAIN_HAND ? GolemModelPaths.BEACON_RIGHT : GolemModelPaths.BEACON_LEFT;
		}

		@Override
		public ResourceLocation getAnimBaseId(MetalGolemEntity golem, ItemStack stack, InteractionHand hand) {
			return hand == InteractionHand.MAIN_HAND ? GolemModelPaths.BEACON_RIGHT : GolemModelPaths.BEACON_LEFT;
		}

		@Override
		public void onTick(MetalGolemEntity golem, ItemStack stack, InteractionHand hand) {
			// cheap gates first: server side, every 5th tick, only while there is a live target
			if (golem.level().isClientSide() || (golem.tickCount + (hand == InteractionHand.MAIN_HAND ? 0 : 2)) % 5 != 0) return;
			LivingEntity target = golem.getTarget();
			if (target == null || !target.isAlive()) return;
			double range = ArcaneConfig.COMMON.shoulderRange.get();
			if (golem.distanceToSqr(target) > range * range || CannonPoseUtil.BEACON_CANNON.isOutOfRange(golem, hand)) return;
			AbstractCaster<?> caster = getSpellCaster(stack);
			if (caster == null || !(golem.level() instanceof ServerLevel sl)) return;
			Spell spell = caster.getSpell();
			if (spell.isEmpty()) return;
			int cap = ArcaneConfig.COMMON.weaponMaxCost.get();
			if (cap > 0 && spell.getCost() > cap) return;
			if (!Arc.ready(golem, COOLDOWN_KEY + hand.ordinal(), ArcaneConfig.COMMON.shoulderCooldown.get())) return;
			Spell s = caster.modifySpellBeforeCasting(sl, golem, hand, spell);
			SpellContext ctx = new SpellContext(sl, s, golem, new LivingCaster(golem), stack);
			new EntitySpellResolver(ctx).onCast(stack, sl);
		}

		@Override
		public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
			super.appendHoverText(stack, ctx, list, flag);
			Tips.text(this, stack, ctx, list, flag);
		}

		@Override
		public java.util.Optional<net.minecraft.world.inventory.tooltip.TooltipComponent> getTooltipImage(ItemStack stack) {
			return Tips.image(this, stack);
		}
	}

	// ---- registration -----------------------------------------------------------------------------------------------

	/** One material for the whole family: modulargolems:arcane_golem_sword / _axe / _spear. */
	private static final IGolemWeaponMaterial MATERIAL = new IGolemWeaponMaterial() {
		@Override
		public int getDamage() {
			return 7;
		}

		@Override
		public String getName() {
			return "arcane";
		}

		@Override
		public Item getIngot() {
			return BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("ars_nouveau", "source_gem"));
		}

		@Override
		public boolean fireResistant() {
			return false;
		}

		@Override
		public Item.Properties modify(Item.Properties p) {
			return withCaster(IGolemWeaponMaterial.super.modify(p));
		}

		@Override
		public IGolemWeaponFactory factory() {
			return Weapon::new;
		}
	};

	static void register() {
		for (GolemWeaponType t : GolemWeaponType.values()) t.buildItem(MATERIAL);
		ModularGolems.REGISTRATE.item("arcane_mecha_bow", Bow::new).tag(ItemTags.BOW_ENCHANTABLE).lang("Arcane Mecha Bow").register();
		ModularGolems.REGISTRATE.item("arcane_shoulder_wand", ShoulderWand::new).lang("Arcane Shoulder Wand").register();
	}

}
