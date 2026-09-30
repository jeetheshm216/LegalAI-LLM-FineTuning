"""Authority ranking engine for Indian legal sources."""

from typing import List, Tuple
from ..models import IndianLegalChunk, AuthorityTier, IndianDocumentType, IndianJurisdictionLevel


class IndianAuthorityRanker:
    """Ranks retrieved legal materials according to the Indian constitutional and statutory hierarchy of authority."""

    TIER_WEIGHTS = {
        AuthorityTier.TIER_1_PRIMARY: 1.5,
        AuthorityTier.TIER_2_REGULATORY_STATE: 1.2,
        AuthorityTier.TIER_3_SECONDARY: 1.0,
    }

    TYPE_WEIGHTS = {
        IndianDocumentType.CONSTITUTION: 1.6,
        IndianDocumentType.ACT: 1.4,
        IndianDocumentType.JUDGMENT: 1.35,
        IndianDocumentType.NOTIFICATION: 1.2,
        IndianDocumentType.REGULATION: 1.15,
        IndianDocumentType.RULE: 1.1,
        IndianDocumentType.CIRCULAR: 1.05,
    }

    COURT_WEIGHTS = {
        "Supreme Court of India": 1.5,
        "High Court": 1.2,
        "Tribunal": 1.0
    }

    def compute_authority_score(self, chunk: IndianLegalChunk, base_relevance_score: float) -> float:
        """Calculates final ranked score blending semantic/keyword relevance with institutional legal authority."""
        tier_weight = self.TIER_WEIGHTS.get(chunk.authority_tier, 1.0)
        type_weight = self.TYPE_WEIGHTS.get(chunk.document_type, 1.0)

        court_weight = 1.0
        if chunk.court:
            for c_name, c_wt in self.COURT_WEIGHTS.items():
                if c_name.lower() in chunk.court.lower():
                    court_weight = c_wt
                    break

        combined_weight = tier_weight * type_weight * court_weight
        return base_relevance_score * combined_weight

    def rank_chunks(
        self,
        chunks_with_scores: List[Tuple[IndianLegalChunk, float]]
    ) -> List[Tuple[IndianLegalChunk, float]]:
        """Sorts and re-ranks a retrieved chunk list by weighted authority score."""
        ranked = []
        for chunk, score in chunks_with_scores:
            auth_score = self.compute_authority_score(chunk, score)
            ranked.append((chunk, auth_score))

        # Sort descending by auth_score
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
