using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 余烬蔓延（EmberSpread）——燎原的死亡传播效果。
/// 当敌人死亡时，将其身上的灼燃层数分配给其他存活敌人。
/// </summary>
[RegisterPower]
public sealed class EmberSpread : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    /// <summary>
    /// 当敌人死亡时触发。将其身上的灼燃层数分配给其他存活敌人。
    /// </summary>
    public override async Task AfterDeath(PlayerChoiceContext choiceContext, Creature creature, bool wasRemovalPrevented, float deathAnimLength)
    {
        if (Amount <= 0) return;
        // Only trigger when enemies die (not the player)
        if (creature == Owner) return;

        // Get the Scorch stacks from the dead enemy
        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(creature);
        if (scorchStacks <= 0) return;

        // Spread to other alive enemies
        var enemies = ReedCombatHelper.GetEnemies(Owner);
        foreach (var enemy in enemies)
        {
            if (enemy != creature && enemy.IsAlive)
                await PowerCmd.Apply<Scorch>(choiceContext, enemy, scorchStacks, Owner, null);
        }
    }
}
