using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 永恒余烬（EternalEmberPower）——先古卡能力。
/// 每回合开始时，对所有敌人施加3层灼燃，并获得等于所有敌人灼燃总层数的格挡。
/// </summary>
[RegisterPower]
public sealed class EternalEmberPower : ModPowerTemplate
{
    private const int ScorchPerTurn = 3;

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (Amount <= 0) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);

        // 对所有敌人施加灼燃
        foreach (var enemy in enemies)
        {
            await PowerCmd.Apply<Scorch>(choiceContext, enemy, ScorchPerTurn, Owner, null);
        }

        // 获得等于所有敌人灼燃总层数的格挡
        int totalScorch = ReedCombatHelper.GetAllEnemiesPowerTotal<Scorch>(Owner);
        if (totalScorch > 0)
        {
            await CreatureCmd.GainBlock(Owner, new BlockVar((decimal)totalScorch, ValueProp.Move), null);
        }
    }
}
