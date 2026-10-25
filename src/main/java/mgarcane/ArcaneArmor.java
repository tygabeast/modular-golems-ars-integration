package mgarcane;

import dev.xkmc.l2core.init.reg.simple.Val;
import dev.xkmc.modulargolems.content.entity.common.AbstractGolemEntity;
import dev.xkmc.modulargolems.content.item.equipments.IGolemModifierItem;
import dev.xkmc.modulargolems.content.item.equipments.MetalGolemArmorItem;
import dev.xkmc.modulargolems.content.modifier.base.GolemModifier;
import dev.xkmc.modulargolems.content.modifier.base.ModifierInstance;
import dev.xkmc.modulargolems.init.ModularGolems;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.function.Supplier;

/**
 * The two Arcane armour sets for Metal Golems, registered through Modular Golems' own registrate like the other Arcane items:
 * Arcane (violet cloth and gold, Source Mantle) and Aegis (ivory plate and gold, Elemental Ward). Each piece worn adds one level
 * of its set's modifier. The shapes are drawn client side by {@link ArmorLayers}; this class never touches client code.
 */
public class ArcaneArmor extends MetalGolemArmorItem implements IGolemModifierItem {

	/** Model path ids; the client registers a matching GolemModelPath for each (see ArmorLayers). */
	public static final ResourceLocation HELMET = path("arcane/helmet"), CHESTPLATE = path("arcane/chestplate"), SHINGUARD = path("arcane/shinguard"), BOOTS = path("arcane/boots");
	public static final ResourceLocation AEGIS_HELMET = path("aegis/helmet"), AEGIS_CHESTPLATE = path("aegis/chestplate"), AEGIS_SHINGUARD = path("aegis/shinguard"), AEGIS_BOOTS = path("aegis/boots");

	private static ResourceLocation path(String s) {
		return ResourceLocation.fromNamespaceAndPath(MGArcane.MODID, s);
	}

	private final Supplier<Val<? extends GolemModifier>> modifier;

	public ArcaneArmor(Item.Properties p, ArmorItem.Type type, int armor, float toughness, ResourceLocation model, Supplier<Val<? extends GolemModifier>> modifier) {
		super(p.stacksTo(1), type, armor, toughness, model);
		this.modifier = modifier;
	}

	@Override
	public List<ModifierInstance> getModifier(ItemStack stack, AbstractGolemEntity<?, ?> golem) {
		return List.of(new ModifierInstance(modifier.get().get(), 1));
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
		super.appendHoverText(stack, ctx, list, flag);
		appendModifierText(stack, list);
	}

	@SafeVarargs
	private static void armor(String name, String lang, ArmorItem.Type type, int armor, float toughness, ResourceLocation model,
							  Supplier<Val<? extends GolemModifier>> mod, TagKey<Item>... tags) {
		ModularGolems.REGISTRATE.item(name, p -> new ArcaneArmor(p, type, armor, toughness, model, mod)).tag(tags).lang(lang).register();
	}

	static void register() {
		// Arcane: diamond tier (11 / 14 / 8 / 6, toughness 6)
		Supplier<Val<? extends GolemModifier>> mantle = () -> ArcaneReg.MANTLE;
		armor("arcane_helmet", "Arcane Cowl", ArmorItem.Type.HELMET, 11, 6f, HELMET, mantle, ItemTags.ARMOR_ENCHANTABLE, ItemTags.HEAD_ARMOR_ENCHANTABLE);
		armor("arcane_chestplate", "Arcane Tunic", ArmorItem.Type.CHESTPLATE, 14, 6f, CHESTPLATE, mantle, ItemTags.ARMOR_ENCHANTABLE, ItemTags.CHEST_ARMOR_ENCHANTABLE);
		armor("arcane_shinguard", "Arcane Sash", ArmorItem.Type.LEGGINGS, 8, 6f, SHINGUARD, mantle, ItemTags.ARMOR_ENCHANTABLE, ItemTags.LEG_ARMOR_ENCHANTABLE);
		armor("arcane_boots", "Arcane Boots", ArmorItem.Type.BOOTS, 6, 6f, BOOTS, mantle, ItemTags.ARMOR_ENCHANTABLE, ItemTags.FOOT_ARMOR_ENCHANTABLE);
		// Aegis: netherite tier (14 / 18 / 10 / 10, toughness 8), the upgrade of the Arcane set
		Supplier<Val<? extends GolemModifier>> ward = () -> ArcaneReg.WARD;
		armor("aegis_helmet", "Aegis Helm", ArmorItem.Type.HELMET, 14, 8f, AEGIS_HELMET, ward, ItemTags.ARMOR_ENCHANTABLE, ItemTags.HEAD_ARMOR_ENCHANTABLE);
		armor("aegis_chestplate", "Aegis Cuirass", ArmorItem.Type.CHESTPLATE, 18, 8f, AEGIS_CHESTPLATE, ward, ItemTags.ARMOR_ENCHANTABLE, ItemTags.CHEST_ARMOR_ENCHANTABLE);
		armor("aegis_shinguard", "Aegis Tassets", ArmorItem.Type.LEGGINGS, 10, 8f, AEGIS_SHINGUARD, ward, ItemTags.ARMOR_ENCHANTABLE, ItemTags.LEG_ARMOR_ENCHANTABLE);
		armor("aegis_boots", "Aegis Boots", ArmorItem.Type.BOOTS, 10, 8f, AEGIS_BOOTS, ward, ItemTags.ARMOR_ENCHANTABLE, ItemTags.FOOT_ARMOR_ENCHANTABLE);
	}

}
