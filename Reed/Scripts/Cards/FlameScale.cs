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
/// 炎鳞（FlameScale）——普通技能牌。
/// 1费，获得5点格挡。若你身上有灼燃，额外获得等同灼燃层数的格挡（最多15）（升级后基础格挡+3）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class FlameScale : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Common;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    private const int MaxBonusBlock = 15;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(5) // 基础格挡
    ];

    public override bool GainsBlock => true;

    public FlameScale() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int scorchStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);
        int bonusBlock = Math.Min(scorchStacks, MaxBonusBlock);
        int blockAmount = DynamicVars.Cards.IntValue + bonusBlock;

        if (blockAmount > 0)
        {
            var block = new BlockVar((decimal)blockAmount, ValueProp.Move);
            await CreatureCmd.GainBlock(Owner.Creature, block, cardPlay);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(3);
}
