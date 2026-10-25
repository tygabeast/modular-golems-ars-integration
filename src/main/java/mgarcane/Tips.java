package mgarcane;

import com.hollingsworth.arsnouveau.api.item.ICasterTool;
import com.hollingsworth.arsnouveau.api.spell.AbstractCaster;
import com.hollingsworth.arsnouveau.client.gui.SpellTooltip;
import com.hollingsworth.arsnouveau.setup.config.Config;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.tooltip.TooltipComponent;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;
import java.util.Optional;

/**
 * Tooltip behaviour shared by every arcane weapon, matching Ars Nouveau's own Enchanter's gear: the scribed spell is shown as
 * glyph icons, and as text names while Shift is held (or when Ars' glyph tooltips are turned off in its config).
 * Only ever called from tooltip code, so this client-side class is never loaded on a dedicated server.
 */
final class Tips {
	private Tips() {}

	static void text(ICasterTool tool, ItemStack stack, Item.TooltipContext ctx, List<Component> list, TooltipFlag flag) {
		if (Screen.hasShiftDown() || !Config.GLYPH_TOOLTIPS.get()) tool.getInformation(stack, ctx, list, flag);
	}

	static Optional<TooltipComponent> image(ICasterTool tool, ItemStack stack) {
		AbstractCaster<?> caster = tool.getSpellCaster(stack);
		if (caster != null && Config.GLYPH_TOOLTIPS.get() && !Screen.hasShiftDown() && !caster.isSpellHidden() && !caster.getSpell().isEmpty())
			return Optional.of(new SpellTooltip(caster));
		return Optional.empty();
	}
}
