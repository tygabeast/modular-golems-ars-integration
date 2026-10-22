package mgarcane;

import dev.xkmc.modulargolems.content.entity.common.AbstractGolemEntity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;

import java.util.List;
import java.util.function.Consumer;

/** Shared helpers. Everything here is allocation-light and server-side only. */
public final class Arc {

	/** Guard so splash damage dealt by a golem does not re-enter its own on-hit abilities (server thread only). */
	public static boolean busy = false;

	private Arc() {
	}

	/** Whether an area ability of this golem may affect e (never the owner, owner's pets, or sibling golems). */
	public static boolean valid(AbstractGolemEntity<?, ?> g, LivingEntity e) {
		if (e == g || !e.isAlive() || g.isAlliedTo(e)) return false;
		LivingEntity owner = g.getOwner();
		if (owner != null && e == owner) return false;
		if (e instanceof AbstractGolemEntity<?, ?> o && g.getOwnerUUID() != null && g.getOwnerUUID().equals(o.getOwnerUUID()))
			return false;
		if (e instanceof TamableAnimal t && owner != null && t.getOwner() == owner) return false;
		return switch (ArcaneConfig.COMMON.targets.get()) {
			case HOSTILE -> e instanceof Enemy;
			case ALL_MOBS -> e instanceof Mob;
			case ALL_MOBS_AND_PLAYERS -> e instanceof Mob || e instanceof Player;
		};
	}

	/** Runs f on every valid entity within r blocks. One list allocation per call; call it on a timer. */
	public static void around(AbstractGolemEntity<?, ?> g, double r, Consumer<LivingEntity> f) {
		around(g, g, r, f);
	}

	/** Same, centred on another entity (e.g. the golem's target). */
	public static void around(AbstractGolemEntity<?, ?> g, Entity c, double r, Consumer<LivingEntity> f) {
		double r2 = r * r;
		List<LivingEntity> list = g.level().getEntitiesOfClass(LivingEntity.class, c.getBoundingBox().inflate(r),
				e -> e != c && e.distanceToSqr(c) <= r2 && valid(g, e));
		for (int i = 0, n = list.size(); i < n; i++) f.accept(list.get(i));
	}

	/** True (and starts the cooldown) when at least `ticks` game ticks passed since this key last fired. */
	public static boolean ready(Entity g, String key, int ticks) {
		CompoundTag pd = g.getPersistentData();
		long now = g.level().getGameTime();
		if (now - pd.getLong(key) < ticks) return false;
		pd.putLong(key, now);
		return true;
	}

	/** True once every `period` ticks, spread over golems by entity id. */
	public static boolean every(AbstractGolemEntity<?, ?> g, int period) {
		return (g.tickCount + g.getId()) % period == 0;
	}

	public static String pct(double v) {
		return Math.round(v * 100) + "%";
	}

}
