package mgarcane;

import dev.xkmc.modulargolems.content.entity.common.AbstractGolemEntity;
import dev.xkmc.modulargolems.content.item.equipments.IGolemModifierItem;
import dev.xkmc.modulargolems.content.item.equipments.MetalGolemArmorItem;
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

/**
 * Arcane Golem armour for Metal Golems: a cowl, tunic, sash and boots of violet cloth and gold. Each piece adds one level of
 * Source Mantle. Registered through Modular Golems' own registrate like the other Arcane items. The shapes are drawn client side
 * by {@link ArmorLayers}; this class never touches client code.
 */
public class ArcaneArmor extends MetalGolemArmorItem implements IGolemModifierItem {

	/** Same tier as Modular Golems' diamond-grade sets: 11 / 14 / 8 / 6 armour, 6 toughness. */
	private static final float TOUGHNESS = 6f;

	/** Model path ids; the client registers a matching GolemModelPath for each (see ArmorLayers). */
	public static final ResourceLocation HELMET = path("helmet"), CHESTPLATE = path("chestplate"), SHINGUARD = path("shinguard"), BOOTS = path("boots");

	private static ResourceLocation path(String s) {
		return ResourceLocation.fromNamespaceAndPath(MGArcane.MODID, "arcane/" + s);
	}

	public ArcaneArmor(Item.Properties p, ArmorItem.Type type, int armor, ResourceLocation model) {
		super(p.stacksTo(1), type, armor, TOUGHNESS, model);
	}

	@Override
	public List<ModifierInstance> getModifier(ItemStack stack, AbstractGolemEntity<?, ?> golem) {
		return List.of(new ModifierInstance(ArcaneReg.MANTLE.get(), 1));
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> list, net.minecraft.world.item.TooltipFlag flag) {
		super.appendHoverText(stack, ctx, list, flag);
		appendModifierText(stack, list);
	}

	@SafeVarargs
	private static void armor(String name, String lang, ArmorItem.Type type, int armor, ResourceLocation model, TagKey<Item>... tags) {
		ModularGolems.REGISTRATE.item(name, p -> new ArcaneArmor(p, type, armor, model)).tag(tags).lang(lang).register();
	}

	static void register() {
		armor("arcane_helmet", "Arcane Cowl", ArmorItem.Type.HELMET, 11, HELMET, ItemTags.ARMOR_ENCHANTABLE, ItemTags.HEAD_ARMOR_ENCHANTABLE);
		armor("arcane_chestplate", "Arcane Tunic", ArmorItem.Type.CHESTPLATE, 14, CHESTPLATE, ItemTags.ARMOR_ENCHANTABLE, ItemTags.CHEST_ARMOR_ENCHANTABLE);
		armor("arcane_shinguard", "Arcane Sash", ArmorItem.Type.LEGGINGS, 8, SHINGUARD, ItemTags.ARMOR_ENCHANTABLE, ItemTags.LEG_ARMOR_ENCHANTABLE);
		armor("arcane_boots", "Arcane Boots", ArmorItem.Type.BOOTS, 6, BOOTS, ItemTags.ARMOR_ENCHANTABLE, ItemTags.FOOT_ARMOR_ENCHANTABLE);
	}

}
