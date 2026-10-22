package mgarcane;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;

@Mod(MGArcane.MODID)
public class MGArcane {

	public static final String MODID = "mg_arcane";

	public MGArcane(IEventBus bus, ModContainer container) {
		container.registerConfig(ModConfig.Type.COMMON, ArcaneConfig.SPEC);
		// Modular Golems is ordered BEFORE this mod, so its registrates already exist.
		ArcaneReg.register();
	}

}
