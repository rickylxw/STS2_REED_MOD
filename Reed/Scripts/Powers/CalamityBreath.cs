using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 灾祸之息（CalamityBreath）—— 焰影苇草的固有能力。
/// 每回合开始时，对所有带有灼燃的敌人施加1层易伤。
/// </summary>
[RegisterPower]
public sealed class CalamityBreath : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    // 玩家回合开始时触发
    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (Amount <= 0) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);
        foreach (var enemy in enemies)
        {
            int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(enemy);
            if (scorchStacks > 0)
            {
                await PowerCmd.Apply<VulnerablePower>(choiceContext, enemy, 1, Owner, null);
            }
        }
    }
}
