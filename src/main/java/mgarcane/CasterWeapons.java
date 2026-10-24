package mgarcane;

import com.hollingsworth.arsnouveau.api.item.ICasterTool;
import com.hollingsworth.arsnouveau.api.spell.AbstractCastMethod;
import com.hollingsworth.arsnouveau.api.spell.AbstractCaster;
import com.hollingsworth.arsnouveau.api.spell.AbstractSpellPart;
import com.hollingsworth.arsnouveau.api.spell.EntitySpellResolver;
import com.hollingsworth.arsnouveau.api.spell.Spell;
import com.hollingsworth.arsnouveau.api.spell.SpellContext;
import com.hollingsworth.arsnouveau.api.spell.wrapped_caster.LivingCaster;
import com.hollingsworth.arsnouveau.common.spell.method.MethodTouch;
import com.hollingsworth.arsnouveau.common.util.PortUtil;
import dev.xkmc.l2damagetracker.contents.attack.DamageData;
import dev.xkmc.modulargolems.content.entity.metalgolem.MetalGolemEntity;
import dev.xkmc.modulargolems.content.item.equipments.IAttackListenerWeapon;
import dev.xkmc.modulargolems.content.item.equipments.MetalGolemWeaponItem;
import dev.xkmc.modulargolems.content.item.ranged.MetalGolemMechaBowItem;
import dev.xkmc.modulargolems.init.ModularGolems;
import dev.xkmc.modulargolems.init.material.GolemWeaponType;
import dev.xkmc.modulargolems.init.material.IGolemWeaponFactory;
import dev.xkmc.modulargolems.init.material.IGolemWeaponMaterial;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.phys.EntityHitResult;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.ProjectileImpactEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Golem weapons that cast an Ars Nouveau spell on hit, set up on the Scribe's Table exactly like the Enchanter's Sword.
 * Ars never charges a non-player caster, so the limit is a per-golem cooldown (and an optional spell cost cap) in the config.
 * This class is only loaded when Ars Nouveau is present.
 */
public final class CasterWeapons {

	private static final String COOLDOWN_KEY = "mg_arcane_cast", ARROW_KEY = "mg_arcane_spell_arrow";

	private CasterWeapons() {
	}

	// ---- shared casting ---------------------------------------------------------------------------------------------

	/** Casts the spell stored on `stack` at `target` on behalf of the golem. Server side, cooldown and cost cap applied. */
	static void cast(LivingEntity golem, ItemStack stack, ICasterTool tool, Entity target) {
		if (!(golem.level() instanceof ServerLevel sl) || target == null || !target.isAlive()) return;
		AbstractCaster<?> caster = tool.getSpellCaster(stack);
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
		List<AbstractSpellPart> list = new ArrayList<>();
		list.add(MethodTouch.INSTANCE);
		list.addAll(spell.recipe);
		spell.recipe = list;
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
			getInformation(stack, ctx, list, flag);
		}
	}

	// ---- ranged -----------------------------------------------------------------------------------------------------

	public static class Bow extends MetalGolemMechaBowItem implements ICasterTool {

		public Bow(Item.Properties p) {
			super(p, 30, 5);
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

		/** Marks every arrow from this bow, so the impact handler knows to cast the spell where it lands. */
		@Override
		public AbstractArrow customArrow(AbstractArrow arrow, ItemStack bow, ItemStack ammo) {
			AbstractArrow a = super.customArrow(arrow, bow, ammo);
			a.getPersistentData().putBoolean(ARROW_KEY, true);
			return a;
		}

		@Override
		public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
			super.appendHoverText(stack, ctx, list, flag);
			getInformation(stack, ctx, list, flag);
		}
	}

	private static void onImpact(ProjectileImpactEvent e) {
		var proj = e.getProjectile();
		if (proj.level().isClientSide() || !proj.getPersistentData().getBoolean(ARROW_KEY)) return;
		if (!(e.getRayTraceResult() instanceof EntityHitResult hit) || !(hit.getEntity() instanceof LivingEntity target)) return;
		if (!(proj.getOwner() instanceof MetalGolemEntity golem)) return;
		ItemStack stack = golem.getMainHandItem();
		if (stack.getItem() instanceof Bow bow) cast(golem, stack, bow, target);
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
		public IGolemWeaponFactory factory() {
			return Weapon::new;
		}
	};

	static void register() {
		for (GolemWeaponType t : GolemWeaponType.values()) t.buildItem(MATERIAL);
		ModularGolems.REGISTRATE.item("arcane_mecha_bow", Bow::new).tag(ItemTags.BOW_ENCHANTABLE).lang("Arcane Mecha Bow").register();
		NeoForge.EVENT_BUS.addListener(CasterWeapons::onImpact);
	}

}
