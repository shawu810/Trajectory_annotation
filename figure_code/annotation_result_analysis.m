load '../evaluation_pop_dist_log10.csv'
subplot(3,1,1)
hist(evaluation_pop_dist_log10(:,2)./evaluation_pop_dist_log10(:,5))
title('dist')

subplot(3,1,2)
hist(evaluation_pop_dist_log10(:,4)./evaluation_pop_dist_log10(:,5))
title('pop')

subplot(3,1,3)
hist(evaluation_pop_dist_log10(:,3)./evaluation_pop_dist_log10(:,5))
title('pop + dist')