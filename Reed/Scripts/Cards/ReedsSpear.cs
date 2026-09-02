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
/// 鑻囪崏涔嬫灙锛圧eedsSpear锛夆€斺�?涓嶅父瑙佹敾鍑荤墝銆?/// 2璐癸紝閫犳垚14鐐逛激瀹筹紙鍗囩骇�?8鐐癸級銆傝嫢鐩爣鏈夌伡鐕冿紝閫犳垚鍙屽€嶄激瀹炽�?/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ReedsSpear : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(14, ValueProp.Move)
    ];

    public ReedsSpear() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int damage = (int)DynamicVars.Damage.BaseValue;
        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);
        if (scorchStacks > 0)
        {
            damage *= 2;
        }

        await DamageCmd.Attack(damage)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}

