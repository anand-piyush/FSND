QUESTIONS_PER_PAGE = 10

def paginate(request, selections):
  """
  max questions per page sliced using the method
  request : arg to get the page number, default 1
  selections : selections that are to be sliced
  """
  page_num = request.args.get('page', 1, type=int)
  start = (page_num-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selections[start:end]]
  return questions
