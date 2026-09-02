using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 灼燃壁垒（ScorchBastion）——常见技能牌。
/// 1费，获得5点格挡，额外格挡为自身灼燃层数×2（升级后基础格挡+3）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchBastion : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Common;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(5m, ValueProp.Move), // 基础格挡
        new CardsVar(2) // 灼燃倍率
    ];

    public override bool GainsBlock => true;

    public ScorchBastion() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int scorchStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);
        int totalBlock = (int)DynamicVars.Block.BaseValue + scorchStacks * DynamicVars.Cards.IntValue;

        if (totalBlock > 0)
        {
            var block = new BlockVar((decimal)totalBlock, ValueProp.Move);
            await CreatureCmd.GainBlock(Owner.Creature, block, cardPlay);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(3);
}
